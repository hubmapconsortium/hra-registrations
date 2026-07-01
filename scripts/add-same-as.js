import { readFileSync, writeFileSync } from 'fs';
import { v4 as uuidV4 } from 'uuid';

function addSameAs(rui_location) {
  rui_location['sameAs'] = rui_location['@id'];
  rui_location['@id'] = `http://purl.org/ccf/1.5/${uuidV4()}`;
  rui_location.placement['@id'] = `${rui_location['@id']}_placement`;
  rui_location.placement.source = undefined;
  return rui_location;
}

const rui_location = JSON.parse(readFileSync(process.argv[2], 'utf-8'));

if (!rui_location.sameAs) {
  addSameAs(rui_location);
}

writeFileSync(process.argv[2], JSON.stringify(rui_location, null, 2));
