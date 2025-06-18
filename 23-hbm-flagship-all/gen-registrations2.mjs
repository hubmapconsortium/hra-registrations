// Requires Node v18+ (for fetch support)
import { writeFileSync } from 'fs';
import Papa from 'papaparse';

const SHEET_ID=process.argv.length > 2 ? process.argv[2] : '1ExZGB0NBLdmihaoDnsjdjwNHD2Lbii048bMkuAWQHbk';
const GID=process.argv.length > 3 ? process.argv[3] : '1414155826';

const CSV_URL=`https://docs.google.com/spreadsheets/d/${SHEET_ID}/export?format=csv&gid=${GID}`;
const FIELDS='dataset_id,source,excluded,paper_id,HuBMAP_tissue_block_id,sample_id,ccf_api_endpoint,CxG_dataset_id_donor_id_organ'.split(',');
const BASE_IRI='https://cns-iu.github.io/hra-cell-type-populations-supporting-information/registrations/rui_locations.jsonld#';
const OUTPUT='rui_locations.jsonld';
const HUBMAP_TOKEN=process.env.HUBMAP_TOKEN;

// A HuBMAP Token is required as some datasets are unpublished
if (!HUBMAP_TOKEN) {
  console.log('Please run `export HUBMAP_TOKEN=xxxYourTokenyyy` and try again.')
  process.exit();
}

// Some rui_locations.jsonld may need to be remapped. You can specify old => new url mappings here.
const ALIASES = {
  'https://dw-dot.github.io/hra-cell-type-populations-rui-json-lds/AllenWangLungMap_rui_locations.jsonld': 'https://cns-iu.github.io/hra-cell-type-populations-rui-json-lds/AllenWangLungMap_rui_locations.jsonld'
}

// Cache for url => retrieved registration data
const dataSourcesCache = {};

/**
 * Grab and normalize registration data from the given url
 * 
 * @param {string} url link to a rui_locations.jsonld to download from 
 * @returns rui_locations.jsonld data (list of donor objects)
 */
async function getDataSource(url) {
  url = ALIASES[url] || url;

  // Add token for HuBMAP's registrations if available
  if (url === 'https://ccf-api.hubmapconsortium.org/v1/hubmap/rui_locations.jsonld' && HUBMAP_TOKEN) {
    url += `?token=${HUBMAP_TOKEN}`; 
  }
  if (!dataSourcesCache[url]) {
    const graph = await fetch(url).then(r => r.json());

    // Normalize results to array of donors
    if (Array.isArray(graph)) {
      dataSourcesCache[url] = graph;
    } else if (graph['@graph']) {
      dataSourcesCache[url] = graph['@graph'];
    } else if (graph['@type']) {
      dataSourcesCache[url] = [ graph ];
    }
  }
  return dataSourcesCache[url];
}

/**
 * Find registration data in a set of registrations given some criteria
 *
 * @param {object[]} data a list of Donor information in the rui_locations.jsonld format 
 * @param { { donorId?, ruiLocation?, sampleId?, datasetId? } } param1 ids to search for
 * @returns returns object with matched donor, block, section, dataset depending on what is matched
 */
function findInData(data, { donorId, ruiLocation, sampleId, datasetId }) {
  for (const donor of data) {
    // If a donor is found, return it
    if (donor['@id'] === donorId) {
      return { donor };
    }

    // Search blocks
    for (const block of donor.samples ?? []) {
      if (block['@id'] === sampleId || block.rui_location['@id'] === ruiLocation) {
        return { donor, block };
      }

      // Search sections
      for (const section of block.sections ?? []) {
        if (section['@id'] === sampleId) {
          return { donor, block, section };
        }

        // Search section datasets
        for (const sectionDataset of section.datasets ?? []) {
          if (sectionDataset['@id'] === datasetId) {
            return { donor, block, section, dataset: sectionDataset };
          }
        }
      }

      // Search block datasets
      for (const blockDataset of block.datasets ?? []) {
        if (blockDataset['@id'] === datasetId) {
          return { donor, block, dataset: blockDataset };
        }
      }
    }
  }
}

/**
 * Get a lookup table that converts given hubmap_ids to (optionally prefixed) UUIDs.
 * If more than 10,000 IDs, please split up into multiple 10k ID calls.
 * 
 * @param {string[]} hubmap_ids a list of hubmap_ids to generate a lookup to Uuid for
 * @param {*} token the hubmap token (for unpublished data)
 * @param {string} prefix prefix for the UUID (often to convert to an HRA-compatible IRI)
 * @returns a lookup table from hubmap_id to (optionally prefixed) UUIDs.
 */
function getHbmToUuidLookup(hubmap_ids, token, prefix = 'https://entity.api.hubmapconsortium.org/entities/') {
  return fetch('https://search.api.hubmapconsortium.org/v3/portal/search', {
    method: 'POST',
    headers: token
      ? { 'Content-type': 'application/json', Authorization: `Bearer ${token}` }
      : { 'Content-type': 'application/json' },
    body: JSON.stringify({
      version: true,
      from: 0,
      size: 10000,
      query: {
        terms: {
          'hubmap_id.keyword': hubmap_ids
        }
      },
      _source: {
        includes: ['uuid', 'hubmap_id'],
      },
    }),
  })
    .then((r) => r.json())
    .then((r) => r.hits.hits.map((n) => n._source))
    .then((r) => r.reduce((acc, row) => (acc[row.hubmap_id] = `${prefix}${row.uuid}`, acc), {}))
}

// Grab the datasets list from the given CSV_URL and convert to array of objects
const allDatasets = await fetch(CSV_URL, { redirect: 'follow' })
  .then((r) => r.text())
  .then((r) =>
    Papa.parse(r, { header: true, fields: FIELDS }).data.filter(
      (row) => row.excluded !== 'TRUE'
    )
  );

const hbmLookup = await getHbmToUuidLookup([
  ...allDatasets.filter(d => d.source === 'HuBMAP').map(d => d.dataset_id),
  ...allDatasets.filter(d => d.source === 'HuBMAP').map(d => d.HuBMAP_tissue_block_id),
], HUBMAP_TOKEN);

const results = [];
const donors = {};
const blocks = {};
const datasets = {};

for (const dataset of allDatasets) {
  // Grab registrations where this dataset occurs in
  const data = await getDataSource(dataset.ccf_api_endpoint);

  let id;
  let result;

  // Custom processing per dataset source (GTEx, HuBMAP, and CxG)
  if (dataset.source === 'GTEx') {
    id = dataset.dataset_id;
    result = findInData(data, { sampleId: dataset.sample_id });
  } else if (dataset.source === 'HuBMAP') {
    id = dataset.dataset_id;
    const datasetId = hbmLookup[id];
    result = findInData(data, { datasetId });
    if (!result) {
      const sampleId = hbmLookup[dataset.HuBMAP_tissue_block_id];
      result = findInData(data, { sampleId });
      if (!result) {
        const datasetLink = id ? `https://portal.hubmapconsortium.org/browse/${id}` : undefined;
        const sampleLink = dataset.HuBMAP_tissue_block_id ? `https://portal.hubmapconsortium.org/browse/${dataset.HuBMAP_tissue_block_id}` : undefined;
        console.log(`Investigate DS: ${datasetLink} => ${datasetId}, \n\t TB: ${sampleLink} => ${sampleId}`);
      } else if (id.trim() === '') {
        id = dataset.HuBMAP_tissue_block_id;
      }
    }
  } else if (dataset.source === 'CxG') {
    id = dataset.CxG_dataset_id_donor_id_organ;
    result = findInData(data, { ruiLocation: dataset.sample_id.split('_')[0] });
    if (!result) {
      const sampleId = dataset.sample_id;
      result = findInData(data, { sampleId });
    }
  }

  // If data is found, add it to the growing list of registrations to output
  if (result) {
    const donorId = result.donor['@id'];
    if (!donors[donorId]) {
      donors[donorId] = {
        '@context': 'https://hubmapconsortium.github.io/ccf-ontology/ccf-context.jsonld',
        ...result.donor,
        samples: []
      };
      results.push(donors[donorId]);
    }
    const donor = donors[donorId];

    const blockId = result.block['@id'];
    if (!blocks[blockId]) {
      blocks[blockId] = {
        ...result.block,
        sections: [],
        datasets: []
      };
      donor.samples.push(blocks[blockId]);
    }
    const block = blocks[blockId];

    const datasetIri = `${BASE_IRI}${id}`
    let hraDataset;
    if (result.dataset) {
      // Copy dataset over with new '@id' matching our dataset id
      hraDataset = Object.assign(
        { '@id': datasetIri }, // makes sure '@id' is first
        result.dataset,
        { '@id': datasetIri }
      );
    } else {
      // If no Dataset was matched, make a new one
      hraDataset = {
        '@id': datasetIri,
        '@type': 'Dataset',
        label: block.label,
        description: block.description,
        link: dataset.paper_id || block.link,
        technology: 'OTHER',
        thumbnail: 'https://cdn.humanatlas.io/ui/ccf-eui/assets/icons/ico-unknown.svg' 
      }
    }
    block.datasets.push(hraDataset);
    datasets[hraDataset['@id']] = hraDataset;
  } else if (dataset.source !== 'HuBMAP' ) { // HuBMAP issues are reported above in more detail
    console.log(`Investigate ${dataset.source}: ${id}`);
  }
}

const savedDatasets = Object.keys(datasets).length;
if (savedDatasets !== allDatasets.length) {
  console.log(`\nThere was some problem saving out at least one dataset. Saved: ${savedDatasets} Expected: ${allDatasets.length}`);
} else {
  console.log(`\nSuccess! Saved: ${savedDatasets}`)
}

// Write out the new rui_locations.jsonld file
writeFileSync(OUTPUT, JSON.stringify(results, null, 2));
