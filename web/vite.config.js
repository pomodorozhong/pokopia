import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(__dirname, '..')

/** Serve / copy repo-root data/ and icons/ into the Vite app. */
function pokopiaAssets() {
  const mime = {
    '.json': 'application/json',
    '.png': 'image/png',
    '.webp': 'image/webp',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
  }

  return {
    name: 'pokopia-assets',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const raw = (req.url || '').split('?')[0]
        if (!raw.startsWith('/data/') && !raw.startsWith('/icons/')) {
          return next()
        }
        const filePath = path.resolve(repoRoot, `.${raw}`)
        if (
          !filePath.startsWith(repoRoot) ||
          !fs.existsSync(filePath) ||
          !fs.statSync(filePath).isFile()
        ) {
          return next()
        }
        const ext = path.extname(filePath).toLowerCase()
        res.setHeader('Content-Type', mime[ext] || 'application/octet-stream')
        fs.createReadStream(filePath).pipe(res)
      })
    },
    closeBundle() {
      const dist = path.resolve(__dirname, 'dist')
      for (const dir of ['data', 'icons']) {
        fs.cpSync(path.join(repoRoot, dir), path.join(dist, dir), {
          recursive: true,
        })
      }
      fs.writeFileSync(path.join(dist, '.nojekyll'), '')
    },
  }
}

export default defineConfig({
  base: './',
  plugins: [react(), pokopiaAssets()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
