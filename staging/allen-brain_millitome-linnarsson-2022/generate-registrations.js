import { readFileSync, writeFileSync } from 'fs';
import { dump } from 'js-yaml';
import Papa from 'papaparse';
import { dirname, join } from 'path';
import sh from 'shelljs';
import { fileURLToPath } from 'url';

const OUTPUT_DIR = dirname(fileURLToPath(import.meta.url));
const ES_PREFIX = 'https://doi.org/10.1126/science.add7046#';
const HRA_MALE_BRAIN_JSON = 'https://cdn.humanatlas.io/digital-objects/ref-organ/brain-male/latest/graph.json';
const HRA_FEMALE_BRAIN_JSON = 'https://cdn.humanatlas.io/digital-objects/ref-organ/brain-female/latest/graph.json';
const ALLEN_PIN_COORDS_CSV = './resources/atlas_pin_coords_ICBM.csv';
const THICKNESS = 10;

const CONSORTIUM_NAME = 'Allen Institute for Brain Science';
const PROVIDER_NAME = 'Allen Institute';
const PROVIDER_UUID = '8dca7930-e16b-4301-9ad3-de202225d27f';
const ALLEN_THUMBNAIL = 'https://hubmapconsortium.github.io/hra-registrations/allen-brain-bakken-2021/assets/logo.jpg';
const ALLEN_LINK = 'https://doi.org/10.1126/science.add7046';
const ALLEN_PUBLICATION = 'https://doi.org/10.1126/science.add7046';

/**
 * Calculate the dimensions of a brain slice based on its volume and thickness.
 * @param {Object} slice - The slice data object.
 * @param {Object} hraBrain - The HRA brain reference object.
 * @returns {Object} Dimensions {x, y, z} in millimeters.
 */
function getDimensions(slice, hraBrain) {
  const volume = parseFloat(slice['polygon_volume(mm^3)']);
  const x = Math.sqrt(volume / THICKNESS);
  const y = Math.sqrt(volume / THICKNESS);

  return { x: x, y: y, z: THICKNESS };
}

/**
 * Calculate the translation coordinates for a brain slice.
 * @param {Object} slice - The slice data object.
 * @param {Object} hraBrain - The HRA brain reference object.
 * @returns {Object} Translation {x, y, z} in millimeters.
 */
function getTranslation(slice, hraBrain) {
  let { pin_MNI_x: x, pin_MNI_y: z, pin_MNI_z: y } = slice;
  const brainDepth = hraBrain.data[0].z_dimension;
  const scaling = 0.5;

  // x = parseFloat(x) * scaling;
  // y = parseFloat(y) * scaling;
  // z = brainDepth - parseFloat(z) * scaling + THICKNESS * 2;

  x = parseFloat(x) * scaling;
  y = parseFloat(y) * scaling;
  z = parseFloat(z) * scaling;
  return { x, y, z };
}

/**
 * Process a single brain slice and generate its registration data structure.
 * @param {Object} slice - The slice data object.
 * @param {string} sex - The sex of the brain (male/female).
 * @param {string} target - The target brain reference ID.
 * @param {Object} hraBrain - The HRA brain reference object.
 * @returns {Object} Registration data for the slice.
 */
function processSlice(slice, sex, target, hraBrain) {
  const today = new Date().toISOString().split('T')[0];
  const { 'Unnamed: 0': id } = slice;
  const { x: x_dimension, y: y_dimension, z: z_dimension } = getDimensions(slice, hraBrain);
  const { x: x_translation, y: y_translation, z: z_translation } = getTranslation(slice, hraBrain);
  const iri = `${ES_PREFIX}${id}_${sex}`;
  return {
    id: `${iri}_DONOR`,
    sex,
    label: `${sex} ${slice['block_id']} ${slice['slice_id']} ${slice['color']}`,
    description: `${id} ${slice['slab_name']}`,
    samples: [
      {
        id: `${iri}_Block`,
        description: id,
        rui_location: {
          '@context': 'https://hubmapconsortium.github.io/ccf-ontology/ccf-context.jsonld',
          '@id': `${iri}`,
          '@type': 'SpatialEntity',
          creator: 'Bruce W. Herr II',
          creator_first_name: 'Bruce',
          creator_last_name: 'Herr',
          creator_orcid: 'https://orcid.org/0000-0002-6703-7647',
          label: id,
          creation_date: today,
          dimension_units: 'millimeter',
          x_dimension,
          y_dimension,
          z_dimension,
          placement: {
            '@context': 'https://hubmapconsortium.github.io/ccf-ontology/ccf-context.jsonld',
            '@id': `${iri}_placement`,
            '@type': 'SpatialPlacement',
            target,
            placement_date: today,
            scaling_units: 'ratio',
            rotation_order: 'XYZ',
            rotation_units: 'degree',
            translation_units: 'millimeter',
            x_scaling: 1.0,
            y_scaling: 1.0,
            z_scaling: 1.0,
            x_rotation: 0.0,
            y_rotation: 0.0,
            z_rotation: 0.0,
            x_translation,
            y_translation,
            z_translation,
          },
        },
      },
    ],
  };
}

/**
 * Build registrations for all slices in the provided HRA brain JSON reference.
 * Writes output files for registrations and extraction sites, and normalizes them.
 * @param {string} hraBrainJson - URL to the HRA brain JSON reference.
 */
async function buildRegistrations(hraBrainJson) {
  const brainRows = Papa.parse(readFileSync(ALLEN_PIN_COORDS_CSV, 'utf8'), { header: true, skipEmptyLines: true }).data;

  const hraBrain = await fetch(hraBrainJson).then((r) => r.json());
  const hraBrainTarget = hraBrain.data[0].id;
  const hraBrainSex = hraBrain.data[0].organ_owner_sex;

  const results = [
    {
      consortium_name: CONSORTIUM_NAME,
      provider_name: PROVIDER_NAME,
      provider_uuid: PROVIDER_UUID,
      defaults: {
        id: ES_PREFIX,
        thumbnail: ALLEN_THUMBNAIL,
        link: ALLEN_LINK,
        publication: ALLEN_PUBLICATION,
      },
      donors: brainRows.map((slice) => processSlice(slice, hraBrainSex, hraBrainTarget, hraBrain)),
    },
  ];

  const outputDir = join(OUTPUT_DIR, hraBrainSex.toLowerCase());
  sh.mkdir('-p', outputDir);

  writeFileSync(
    join(outputDir, 'registrations.yaml'),
    `# yaml-language-server: $schema=https://raw.githubusercontent.com/hubmapconsortium/hra-rui-locations-processor/main/registrations.schema.json

${dump(results)}`
  );

  const extraction_sites = results[0].donors.map((donor) => donor.samples[0].rui_location);
  writeFileSync(join(outputDir, 'extraction_sites.json'), JSON.stringify(extraction_sites, null, 2));

  sh.exec(`npx -y github:hubmapconsortium/hra-rui-locations-processor normalize ${outputDir}`);
}

await buildRegistrations(HRA_FEMALE_BRAIN_JSON);
await buildRegistrations(HRA_MALE_BRAIN_JSON);
