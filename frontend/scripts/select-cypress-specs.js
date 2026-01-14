const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function readSpecMap(mapPath) {
  const raw = fs.readFileSync(mapPath, 'utf8');
  return JSON.parse(raw);
}

function resolveRepoRoot() {
  try {
    return execSync('git rev-parse --show-toplevel', { encoding: 'utf8' }).trim();
  } catch (err) {
    return process.cwd();
  }
}

function resolveBaseRef(repoRoot, baseRef) {
  try {
    execSync(`git rev-parse --verify ${baseRef}`, { cwd: repoRoot, stdio: 'ignore' });
    return baseRef;
  } catch (err) {
    return 'HEAD~1';
  }
}

function getChangedFiles(repoRoot, baseRef) {
  try {
    const output = execSync(`git diff --name-only ${baseRef}...HEAD`, {
      cwd: repoRoot,
      encoding: 'utf8',
    }).trim();
    return output ? output.split('\n') : [];
  } catch (err) {
    return [];
  }
}

function matchSpecs(changedFiles, mappings) {
  const specs = new Set();
  changedFiles.forEach((file) => {
    mappings.forEach((mapping) => {
      if (mapping.paths.some((prefix) => file.startsWith(prefix))) {
        mapping.specs.forEach((spec) => specs.add(spec));
      }
    });
  });
  return specs;
}

function main() {
  const repoRoot = resolveRepoRoot();
  const mapPath = path.join(repoRoot, 'frontend', 'cypress', 'spec-map.json');
  const specMap = readSpecMap(mapPath);
  const baseRef = resolveBaseRef(repoRoot, process.env.CYPRESS_BASE_REF || 'origin/master');
  const changedFiles = getChangedFiles(repoRoot, baseRef);
  const matchedSpecs = matchSpecs(changedFiles, specMap.mappings || []);

  if (matchedSpecs.size === 0) {
    const fallback = specMap.defaultSpecs || ['cypress/e2e/**/*.js'];
    process.stdout.write(fallback.join(','));
    return;
  }

  process.stdout.write([...matchedSpecs].join(','));
}

main();
