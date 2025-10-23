#!/usr/bin/env node
/**
 * @file generate-brain-registrations.js
 * @description Generate HRA brain registrations from Allen Institute CSV data.
 */

import { Command } from 'commander';
import { accessSync, constants as fsConstants, readFileSync, statSync, writeFileSync } from 'fs';
import { dump } from 'js-yaml';
import Papa from 'papaparse';
import { join } from 'path';
import sh from 'shelljs';

const program = new Command();

/* ----------------------------- CLI Definition ----------------------------- */
/**
 * CLI arguments and options definition using Commander.
 *
 * Required positional arguments:
 *   - ALLEN_PIN_COORDS_CSV: CSV of Allen Institute pin coordinates
 *   - OUTPUT_DIR: Directory to output the generated registration files
 *
 * Optional flags (with defaults):
 *   - --id-prefix
 *   - --consortium-name
 *   - --provider-name
 *   - --provider-uuid
 *   - --thumbnail
 *   - --link
 *   - --publication
 *   - --slab-thickness
 *   - --duplicate-donors / --no-duplicate-donors
 */
program
  .name('generate-brain-registrations')
  .description('Generate HRA brain registrations from Allen Institute pin coordinates CSV.')
  .argument('<ALLEN_PIN_COORDS_CSV>', 'Path to Allen Institute pin coordinates CSV file')
  .argument('<OUTPUT_DIR>', 'Directory to output registration files')
  .option('--id-prefix <string>', 'IRI prefix for generated IDs', 'https://doi.org/10.1126/science.add7046#')
  .option('--consortium-name <string>', 'Name of the consortium', 'Allen Institute for Brain Science')
  .option('--provider-name <string>', 'Provider name', 'Allen Institute')
  .option('--provider-uuid <uuid>', 'Provider UUID', '8dca7930-e16b-4301-9ad3-de202225d27f')
  .option('--structure-name <string>', 'Structure Name column for labeling', 'Siletti_name')
  .option(
    '--thumbnail <url>',
    'Thumbnail image URL',
    'https://hubmapconsortium.github.io/hra-registrations/allen-brain-bakken-2021/assets/logo.jpg'
  )
  .option('--link <url>', 'Dataset link', 'https://doi.org/10.1126/science.add7046')
  .option('--publication <url>', 'Publication link', 'https://doi.org/10.1126/science.add7046')
  .option('--slab-thickness <number>', 'Thickness of each brain slab in mm', '10')
  .option('--duplicate-donors', 'Duplicate donors for a more informative EUI (default: true)', true)
  .option('--no-duplicate-donors', 'Disable donor duplication (IDs use donor_name only)')
  .showHelpAfterError('(use --help for usage information)')
  .parse(process.argv);

const options = program.opts();
const [ALLEN_PIN_COORDS_CSV, OUTPUT_DIR] = program.args;

/* --------------------------- CLI Option Constants -------------------------- */
const ID_PREFIX = options.idPrefix;
const CONSORTIUM_NAME = options.consortiumName;
const PROVIDER_NAME = options.providerName;
const PROVIDER_UUID = options.providerUuid;
const THUMBNAIL = options.thumbnail;
const LINK = options.link;
const PUBLICATION = options.publication;
const SLAB_THICKNESS = +options.slabThickness;
const DUPLICATE_DONORS = !!options.duplicateDonors;
const STRUCTURE_NAME = options.structureName;

if (Number.isNaN(SLAB_THICKNESS) || SLAB_THICKNESS <= 0) {
  console.error(`Invalid --slab-thickness: must be a positive number.`);
  process.exit(1);
}

/* ------------------------------- Fixed URLs -------------------------------- */
const HRA_MALE_BRAIN_JSON = 'https://cdn.humanatlas.io/digital-objects/ref-organ/brain-male/latest/graph.json';
const HRA_FEMALE_BRAIN_JSON = 'https://cdn.humanatlas.io/digital-objects/ref-organ/brain-female/latest/graph.json';

/* ------------------------------- Validation -------------------------------- */
/**
 * Exit with a friendly message.
 * @param {string} message - The error message.
 * @param {number} [code=1] - Exit code.
 */
function exitWithError(message, code = 1) {
  console.error(`Error: ${message}`);
  process.exit(code);
}

/**
 * Check that a path exists and is readable.
 * @param {string} path - Path to file.
 */
function validateInputFile(path) {
  try {
    const s = statSync(path);
    if (!s.isFile()) exitWithError(`Expected a file but found something else at "${path}".`);
    accessSync(path, fsConstants.R_OK);
  } catch (err) {
    exitWithError(`Cannot access input file "${path}": ${err.message}`);
  }
}

/**
 * Ensure output directory exists and is writable.
 * @param {string} dir - Directory path.
 */
function ensureOutputDirectory(dir) {
  try {
    sh.mkdir('-p', dir);
    const s = statSync(dir);
    if (!s.isDirectory()) exitWithError(`Output path "${dir}" exists but is not a directory.`);
    accessSync(dir, fsConstants.W_OK);
  } catch (err) {
    exitWithError(`Cannot prepare output directory "${dir}": ${err.message}`);
  }
}

/* ------------------------------- Core Logic -------------------------------- */
/**
 * Calculate dimensions of a brain slice.
 * @param {Object} slice - Slice data row.
 * @returns {{x:number, y:number, z:number}} Dimensions in millimeters.
 */
function getDimensions(slice) {
  const volume = parseFloat(slice['polygon_volume(mm^3)']);
  if (Number.isNaN(volume) || volume <= 0) {
    return { x: SLAB_THICKNESS, y: SLAB_THICKNESS, z: SLAB_THICKNESS };
  }
  const x = Math.sqrt(volume / SLAB_THICKNESS);
  const y = Math.sqrt(volume / SLAB_THICKNESS);
  return { x, y, z: SLAB_THICKNESS };
}

/**
 * Compute the MNI origin for a given HRA brain.
 * @param {Object} hraBrain - Parsed HRA brain graph.json.
 * @returns {{x:number, y:number, z:number}} Origin coordinates in mm.
 */
function getMNIOrigin(hraBrain) {
  const brain = hraBrain.data[0];
  const ac = hraBrain.data.find(
    (entity) =>
      entity.representation_of === 'UBERON:0000935' &&
      entity.object_reference.file_subpath === 'Allen_anterior_commissure_L'
  );

  if (!ac) {
    const bp = brain.object_reference.placement;
    return { x: bp.x_translation, y: bp.y_translation, z: bp.z_translation };
  }

  const bp = brain.object_reference.placement;
  const acp = ac.object_reference.placement;
  return {
    x: bp.x_translation - acp.x_translation + (ac.x_dimension || 0),
    y: bp.y_translation - acp.y_translation + (ac.y_dimension || 0) / 2,
    z: bp.z_translation - acp.z_translation + (ac.z_dimension || 0) / 2,
  };
}

/**
 * Compute translation for slice placement.
 * @param {Object} slice - CSV slice data row.
 * @param {Object} hraBrain - HRA brain object.
 * @returns {{x:number, y:number, z:number}} Translation vector.
 */
function getTranslation(slice, hraBrain) {
  // Coordinates are in MNI / LPS space in mm from the AC
  // - LPS: +x = Left,  +y = Posterior, +z = Superior
  // - CCF: +X = Right, +Y = Superior,  +Z = Anterior
  let x = parseFloat(slice.MNI_x_mm);
  let y = parseFloat(slice.MNI_y_mm);
  let z = parseFloat(slice.MNI_z_mm);
  const hemisphere = (slice.dissected_hemisphere || '').trim().toLowerCase();

  if (Number.isNaN(x)) x = 0;
  if (Number.isNaN(y)) y = 0;
  if (Number.isNaN(z)) z = 0;

  const origin = getMNIOrigin(hraBrain);
  const scalar = 0.9;
  if (hemisphere === 'left') x = -x; // flip X to get it on the left hemisphere

  return {
    x: -x * scalar + origin.x, // flip Left→Right
    y: +z * scalar + origin.y, // Superior is shared, remap axis
    z: -y * scalar + origin.z, // flip Posterior→Anterior
  };
}

/**
 * Process one brain slice into a donor registration.
 * @param {Object} slice - Slice data.
 * @param {string} sex - 'male' or 'female'.
 * @param {string} target - Target brain reference ID.
 * @param {Object} hraBrain - HRA brain data.
 * @param {boolean} [duplicateDonors=false] - Whether to duplicate donor entries.
 * @returns {Object} Donor registration object.
 */
function processSlice(slice, sex, target, hraBrain, duplicateDonors = false) {
  const today = new Date().toISOString().split('T')[0];
  const { pin_nhash_id: id, donor_name } = slice;
  const { x: x_dimension, y: y_dimension, z: z_dimension } = getDimensions(slice);
  const { x: x_translation, y: y_translation, z: z_translation } = getTranslation(slice, hraBrain);
  const age = +slice['donor_age_years'] || undefined;
  const iri = `${ID_PREFIX}${id}_${sex}`;

  return {
    id: duplicateDonors ? `${ID_PREFIX}${donor_name}_${id}` : `${ID_PREFIX}${donor_name}`,
    sex,
    age,
    label: age ? `${sex}, Age ${age}, ${donor_name}` : `${sex}, ${donor_name}`,
    description: duplicateDonors ? `${slice[STRUCTURE_NAME]}, ${id}` : undefined,
    samples: [
      {
        id: `${iri}_Block`,
        description: duplicateDonors ? undefined : `${slice[STRUCTURE_NAME]}, ${id}`,
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
 * Build registration outputs from CSV and HRA reference data.
 */
async function buildRegistrations() {
  validateInputFile(ALLEN_PIN_COORDS_CSV);
  ensureOutputDirectory(OUTPUT_DIR);

  console.log(`Reading CSV: ${ALLEN_PIN_COORDS_CSV}`);
  const csvText = readFileSync(ALLEN_PIN_COORDS_CSV, 'utf8');
  const brainRows = Papa.parse(csvText, { header: true, skipEmptyLines: true }).data;

  console.log('Fetching HRA brain references...');
  let hraMaleBrain, hraFemaleBrain;
  try {
    hraMaleBrain = await fetch(HRA_MALE_BRAIN_JSON).then((r) => r.json());
    hraFemaleBrain = await fetch(HRA_FEMALE_BRAIN_JSON).then((r) => r.json());
  } catch (err) {
    exitWithError(`Unable to fetch HRA brain JSONs: ${err.message}`);
  }

  const donors = [];
  for (const slice of brainRows) {
    const sexField = (slice.donor_sex || '').trim().toLowerCase();
    const hraBrain = sexField === 'male' ? hraMaleBrain : hraFemaleBrain;
    const hraBrainTarget = hraBrain.data?.[0]?.id;
    const hraBrainSex = hraBrain.data?.[0]?.organ_owner_sex || sexField;

    if (!hraBrainTarget) {
      console.warn(`Skipping row (no valid HRA brain target): ${slice.pin_nhash_id}`);
      continue;
    }

    try {
      donors.push(processSlice(slice, hraBrainSex, hraBrainTarget, hraBrain, DUPLICATE_DONORS));
    } catch (err) {
      console.warn(`Failed to process slice ${slice.pin_nhash_id}: ${err.message}`);
    }
  }

  const results = [
    {
      consortium_name: CONSORTIUM_NAME,
      provider_name: PROVIDER_NAME,
      provider_uuid: PROVIDER_UUID,
      defaults: {
        id: ID_PREFIX,
        thumbnail: THUMBNAIL,
        link: LINK,
        publication: PUBLICATION,
      },
      donors,
    },
  ];

  // Write registrations.yaml
  writeFileSync(
    join(OUTPUT_DIR, 'registrations.yaml'),
    `# yaml-language-server: $schema=https://raw.githubusercontent.com/hubmapconsortium/hra-rui-locations-processor/main/registrations.schema.json\n\n${dump(
      results
    )}`
  );

  // Write extraction_sites.json
  const extraction_sites = results[0].donors.map((d) => d.samples[0].rui_location);
  writeFileSync(join(OUTPUT_DIR, 'extraction_sites.json'), JSON.stringify(extraction_sites, null, 2));

  // Normalize
  sh.exec(`npx -y github:hubmapconsortium/hra-rui-locations-processor normalize --add-collisions ${OUTPUT_DIR}`);

  // Patch index.html
  try {
    const indexPath = join(OUTPUT_DIR, 'index.html');
    const html = readFileSync(indexPath, 'utf-8').replace(
      `// eui.selectedOrgans = [ 'http://purl.obolibrary.org/obo/UBERON_0002097' ];`,
      `eui.selectedOrgans = [
            'http://purl.obolibrary.org/obo/UBERON_0002097',
            'http://purl.obolibrary.org/obo/UBERON_0000955',
          ];`
    );
    writeFileSync(indexPath, html);
  } catch {
    console.warn('index.html not found (may be generated later).');
  }

  console.log(`✅ All done — outputs written to: ${OUTPUT_DIR}`);
}

/* ------------------------------- Entrypoint -------------------------------- */
(async () => {
  if (!ALLEN_PIN_COORDS_CSV || !OUTPUT_DIR) {
    program.outputHelp();
    process.exit(1);
  }

  try {
    await buildRegistrations();
  } catch (err) {
    exitWithError(`Unexpected error: ${err?.message || err}`);
  }
})();
