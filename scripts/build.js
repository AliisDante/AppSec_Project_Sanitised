const process = require("node:process");
const esbuild = require("esbuild");
const sassPlugin = require("esbuild-sass-plugin");

esbuild
  .build({
    entryPoints: [process.argv[2]],
    bundle: true,
    // minify: true,
    outfile: process.argv[3],
    plugins: [sassPlugin.sassPlugin()],
  })
  .catch((e) => console.error(e.message));
