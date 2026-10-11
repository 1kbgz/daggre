import { bundle } from "./tools/bundle.mjs";
import { bundle_css } from "./tools/css.mjs";
import { node_modules_external } from "./tools/externals.mjs";

import fs from "fs";
import cpy from "cpy";

const BUNDLES = [
  {
    entryPoints: ["src/index.js", "src/anywidget.js"],
    outdir: "dist/static",
  },
  {
    entryPoints: ["src/index.js"],
    plugins: [node_modules_external()],
    outfile: "dist/esm/index.js",
  },
  {
    entryPoints: ["src/index.js"],
    outfile: "dist/cdn/index.js",
  },
];

async function build() {
  fs.rmSync("dist", { recursive: true, force: true });
  fs.rmSync("../daggre/extension", {
    recursive: true,
    force: true,
  });

  // Bundle css
  await bundle_css();

  // Copy HTML
  await cpy("src/html/*", "dist/");

  // Copy images
  if (fs.existsSync("src/img")) {
    fs.mkdirSync("dist/img", { recursive: true });
    await cpy("src/img/*", "dist/img");
  }

  await Promise.all(BUNDLES.map(bundle)).catch(() => process.exit(1));

  fs.copyFileSync(
    "node_modules/@1kbgz/transports/dist/pkg/transports_bg.wasm",
    "dist/static/transports_bg.wasm",
  );
  await cpy("dist/static/*", "../daggre/static");

  // Copy servable assets to python extension (exclude esm/)
  fs.mkdirSync("../daggre/extension", { recursive: true });
  await cpy("dist/**/*", "../daggre/extension", {
    filter: (file) =>
      !file.relativePath.startsWith("esm/") &&
      !file.relativePath.startsWith("dist/esm/"),
  });
}

await build();
