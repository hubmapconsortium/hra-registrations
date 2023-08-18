import { readFileSync, writeFileSync } from 'fs';
import * as glob from 'glob';
import Papa from 'papaparse';

const OUTPUT = 'registrations-report.csv';
const reports = glob.sync('*/**/report.csv');

const merged = [];
for (const report of reports) {
  const rows = Papa.parse(readFileSync(report).toString(), { header: true, skipEmptyLines: true }).data;
  const name = report.split('/').slice(0, -1).join('/');

  for (const row of rows) {
    merged.push({
      name,
      ...row,
    });
  }
}

writeFileSync(OUTPUT, Papa.unparse(merged, { header: true }));
