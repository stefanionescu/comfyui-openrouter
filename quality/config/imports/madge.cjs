var path = require('node:path');

module.exports = {
  resolve: {
    alias: {
      // ComfyUI supplies these modules; the graph follows their declared host boundary.
      '../../scripts/app.js$': path.resolve(process.cwd(), 'web/scripts/host.d.ts'),
      '../../scripts/api.js$': path.resolve(process.cwd(), 'web/scripts/host.d.ts'),
      '#styles': path.resolve(process.cwd(), 'web/styles'),
      '#web': path.resolve(process.cwd(), 'web/scripts'),
    },
    extensions: ['.ts', '.js', '.mjs', '.json'],
  },
};
