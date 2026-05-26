#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f Gemfile ]]; then
  echo "SKIP: no Gemfile found"
  exit 0
fi

bundle install
bundle exec jekyll build --trace

test -d _site
test -f _site/index.html

echo "PASS: Jekyll build smoke"
