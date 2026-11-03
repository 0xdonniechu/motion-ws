#!/usr/bin/env bash
# Kiểm nhanh (không render): token, catalog, theme, tua (seek) và trial-night khớp trial. Chạy từ gốc repo:
#   JSDOM_DIR=/tmp/jsdom-env bash jobs/20261103-corp-demo-dashboard/verify.sh      # jsdom cài một lần ngoài repo: (cd /tmp/jsdom-env && npm i jsdom)
set -e
P=presets/corporate-motion; J=jobs/20261103-corp-demo-dashboard
node --check server.js
node $P/kit/build-tokens.mjs --check
node $P/kit/build-tokens.mjs --check --theme night --out $P/kit/tokens.night.js
node $P/kit/build-tokens.mjs --check-style
node $P/kit/build-tokens.mjs --check-catalog
node $P/kit/build-tokens.mjs --check-scenes $P/demo/index.html $J/trial/index.html $J/full/index.html
cmp $J/trial/index.html $J/trial-night/index.html && echo "trial-night/index.html giống trial/index.html (chỉ tokens.js khác)"
test "$(readlink $J/trial-night/tokens.js)" = "../../../$P/kit/tokens.night.js" && echo "trial-night/tokens.js -> tokens.night.js"
for d in $P/demo $J/trial $J/full; do node $P/demo/seek-test.mjs $d/index.html 0.4; done
