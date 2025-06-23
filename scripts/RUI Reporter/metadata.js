import { checkFetchResponse } from '../util/fs.js';

// Code mappings derived from:
// https://ontology.api.hubmapconsortium.org/organs?application_context=HUBMAP
// https://ontology.api.hubmapconsortium.org/organs?application_context=SENNET
export const ORGAN_MAPPING = {
  AD: {
    code: 'AD',
    label: 'Adipose Tissue',
    organ_id: 'UBERON:0001013',
  },
  AO: {
    code: 'AO',
    label: 'Aorta',
    organ_id: 'UBERON:0000947',
  },
  BD: {
    code: 'BD',
    label: 'Blood',
    organ_id: 'UBERON:0000178',
  },
  BL: {
    code: 'BL',
    label: 'Bladder',
    organ_id: 'UBERON:0001255',
  },
  BM: {
    code: 'BM',
    label: 'Bone Marrow',
    organ_id: 'UBERON:0002371',
  },
  BR: {
    code: 'BR',
    label: 'Brain',
    organ_id: 'UBERON:0000955',
  },
  BS: {
    code: 'BS',
    label: 'Breast',
    organ_id: 'UBERON:0000310', // mammary gland? UBERON:0001911
  },
  BX: {
    code: 'BX',
    label: 'Bone',
    // No trained model as of 2/22/24
    organ_id: 'UBERON:0001474',
  },
  HT: {
    code: 'HT',
    label: 'Heart',
    organ_id: 'UBERON:0000948',
  },
  LB: {
    code: 'LB',
    label: 'Bronchus (Left)',
    organ_id: 'UBERON:0002178',
  },
  LE: {
    code: 'LE',
    label: 'Eye (Left)',
    organ_id: 'UBERON:0004548',
  },
  LF: {
    code: 'LF',
    label: 'Fallopian Tube (Left)',
    // No trained model as of 2/22/24
    organ_id: 'UBERON:0001303',
  },
  LI: {
    code: 'LI',
    label: 'Large Intestine',
    organ_id: 'UBERON:0000059',
  },
  LK: {
    code: 'LK',
    label: 'Kidney (Left)',
    organ_id: 'UBERON:0004538',
  },
  LL: {
    code: 'LL',
    label: 'Lung (Left)',
    organ_id: 'UBERON:0002168',
  },
  LN: {
    code: 'LN',
    label: 'Lymph Node',
    organ_id: 'UBERON:0000029', // mesenteric? UBERON:0002509
  },
  LO: {
    code: 'LO',
    label: 'Ovary (Left)',
    // No trained model as of 2/22/24
    organ_id: 'UBERON:0002119',
  },
  LV: {
    code: 'LV',
    label: 'Liver',
    organ_id: 'UBERON:0002107',
  },
  LY: {
    code: 'LY',
    label: 'Lymph Node',
    organ_id: 'UBERON:0000029',
  },
  MU: {
    code: 'MU',
    label: 'Muscle',
    organ_id: 'UBERON:0005090',
  },
  OT: {
    code: 'OT',
    label: 'Other',
    organ_id: undefined,
  },
  PA: {
    code: 'PA',
    label: 'Pancreas',
    organ_id: 'UBERON:0001264',
  },
  PL: {
    code: 'PL',
    label: 'Placenta',
    // No trained model as of 2/22/24
    organ_id: 'UBERON:0001987',
  },
  RB: {
    code: 'RB',
    label: 'Bronchus (Right)',
    organ_id: 'UBERON:0002177',
  },
  RE: {
    code: 'RE',
    label: 'Eye (Right)',
    organ_id: 'UBERON:0004549',
  },
  RF: {
    code: 'RF',
    label: 'Fallopian Tube (Right)',
    // No trained model as of 2/22/24
    organ_id: 'UBERON:0001302',
  },
  RK: {
    code: 'RK',
    label: 'Kidney (Right)',
    organ_id: 'UBERON:0004539',
  },
  RL: {
    code: 'RL',
    label: 'Lung (Right)',
    organ_id: 'UBERON:0002167',
  },
  RN: {
    code: 'RN',
    label: 'Knee (Right)',
    // No trained model as of 2/22/24
    organ_id: 'FMA:24977',
  },
  RO: {
    code: 'RO',
    label: 'Ovary (Right)',
    // No trained model as of 2/22/24
    organ_id: 'UBERON:0002118',
  },
  SI: {
    code: 'SI',
    label: 'Small Intestine',
    organ_id: 'UBERON:0002108',
  },
  SK: {
    code: 'SK',
    label: 'Skin',
    organ_id: 'UBERON:0002097',
  },
  SP: {
    code: 'SP',
    label: 'Spleen',
    organ_id: 'UBERON:0002106',
  },
  ST: {
    code: 'ST',
    label: 'Sternum',
    // No trained model as of 2/22/24
    organ_id: 'UBERON:0000975',
  },
  TH: {
    code: 'TH',
    label: 'Thymus',
    organ_id: 'UBERON:0002370',
  },
  TR: {
    code: 'TR',
    label: 'Trachea',
    organ_id: 'UBERON:0003126',
  },
  UR: {
    code: 'UR',
    label: 'Ureter',
    // No trained model as of 2/22/24
    organ_id: 'UBERON:0000056',
  },
  UT: {
    code: 'UT',
    label: 'Uterus',
    organ_id: 'UBERON:0000995',
  },
  VL: {
    code: 'VL',
    label: 'Lymphatic Vasculature',
    // No trained model as of 2/22/24
    organ_id: 'UBERON:0001473',
  },
};

export function getHeaders(token) {
  const headers = {
    'Content-type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

function getBody(ids, id_keyword, fields) {
  return {
    version: true,
    from: 0,
    size: 10000,
    query: {
      terms: {
        [`${id_keyword}.keyword`]: ids,
      },
    },
    _source: {
      includes: fields,
    },
  };
}

/**
 * Handles 303 responses from the search api.
 * A 303 response is returned when the resulting query is to large for the
 * search api. Instead it returns a temporary url from which to download the result.
 *
 * @param {Response} resp
 * @returns {Promise<Response>}
 */
async function handle303Response(resp) {
  const text = await resp.text();
  if (text.startsWith('https')) {
    return await fetch(text);
  }

  return resp;
}

export async function getMetadata(ids, url, token, id_keyword, fields) {
  let resp = await fetch(url, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify(getBody(ids, id_keyword, fields)),
  });
  if (resp.status === 303) {
    resp = await handle303Response(resp);
  }

  checkFetchResponse(resp, 'Failed to fetch metadata');
  const result = await resp.json();
  return result;
}

export function getSampleBlockId(ancestors, url_prefix) {
  for (const ancestor of ancestors) {
    if (ancestor['entity_type'].toLowerCase() == 'sample' && ancestor['sample_category'].toLowerCase() == 'block') {
      return {
        block_id: `${url_prefix}${ancestor['uuid']}`,
        rui_location: ancestor['rui_location'] ?? '',
      };
    }
  }

  return {};
}

export function getSampleSectionId(ancestors, url_prefix) {
  for (const ancestor of ancestors) {
    if (
      ancestor['entity_type'].toLowerCase() == 'sample' &&
      ancestor['sample_category'].toLowerCase().replace('suspension', 'section') == 'section'
    ) {
      return `${url_prefix}${ancestor['uuid']}`;
    }
  }

  return '';
}
