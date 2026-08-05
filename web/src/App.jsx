import { useEffect, useState } from 'react'
import { LANG_KEY, assetUrl, htmlLang, t } from './i18n'
import PokemonPicker from './components/PokemonPicker'
import ResultsPanel from './components/ResultsPanel'
import SimilarPokemonResults from './components/SimilarPokemonResults'
import './App.css'

export default function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [lang, setLang] = useState(
    () => localStorage.getItem(LANG_KEY) || 'en',
  )
  const [mode, setMode] = useState('mode1')
  const [selected, setSelected] = useState(() => new Set())
  const [query, setQuery] = useState('')
  const [minScore, setMinScore] = useState(2)

  useEffect(() => {
    document.documentElement.lang = htmlLang(lang)
  }, [lang])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const res = await fetch(assetUrl('data/planner.json'))
        if (!res.ok) throw new Error(`Failed to load planner data (${res.status})`)
        const json = await res.json()
        json.pokemon.sort((a, b) => a.name_en.localeCompare(b.name_en))
        if (!cancelled) setData(json)
      } catch (err) {
        console.error(err)
        if (!cancelled) setError(err.message || String(err))
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  function changeLang(next) {
    setLang(next)
    localStorage.setItem(LANG_KEY, next)
  }

  function togglePokemon(name) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(name)) next.delete(name)
      else next.add(name)
      return next
    })
  }

  function removePokemon(name) {
    setSelected((prev) => {
      const next = new Set(prev)
      next.delete(name)
      return next
    })
  }

  function clearSelection() {
    setSelected(new Set())
  }

  const ledeKey = mode === 'mode2' ? 'mode2_lede' : 'mode1_lede'

  return (
    <>
      <div className="page-bg" aria-hidden="true" />

      <div className="app">
        <header className="topbar">
          <div className="brand">
            <p className="brand-mark">Pokopia</p>
            <h1>Living Area Planner</h1>
          </div>
          <div className="topbar-actions">
            <label className="lang-label" htmlFor="lang-select">
              {t(lang, 'lang_label')}
            </label>
            <select
              id="lang-select"
              className="lang-select"
              aria-label={t(lang, 'lang_label')}
              value={lang}
              onChange={(e) => changeLang(e.target.value)}
            >
              <option value="en">English</option>
              <option value="ja">日本語</option>
              <option value="zh_tw">繁體中文</option>
            </select>
          </div>
        </header>

        <nav className="mode-tabs" aria-label="Planner modes">
          <button
            className={`mode-tab${mode === 'mode1' ? ' is-active' : ''}`}
            type="button"
            aria-current={mode === 'mode1' ? 'page' : undefined}
            onClick={() => setMode('mode1')}
          >
            <span className="mode-num">{t(lang, 'mode1_num')}</span>
            <span className="mode-title">{t(lang, 'mode1_title')}</span>
          </button>
          <button
            className={`mode-tab${mode === 'mode2' ? ' is-active' : ''}`}
            type="button"
            aria-current={mode === 'mode2' ? 'page' : undefined}
            onClick={() => setMode('mode2')}
          >
            <span className="mode-num">{t(lang, 'mode2_num')}</span>
            <span className="mode-title">{t(lang, 'mode2_title')}</span>
          </button>
        </nav>

        <p className="lede">
          {error ? t(lang, 'load_error') : t(lang, ledeKey)}
        </p>

        {data ? (
          <main className="layout">
            <PokemonPicker
              data={data}
              lang={lang}
              selected={selected}
              query={query}
              onQueryChange={setQuery}
              onToggle={togglePokemon}
              onRemove={removePokemon}
              onClear={clearSelection}
            />
            {mode === 'mode2' ? (
              <SimilarPokemonResults
                data={data}
                lang={lang}
                selected={selected}
                minScore={minScore}
                onMinScoreChange={setMinScore}
              />
            ) : (
              <ResultsPanel
                data={data}
                lang={lang}
                selected={selected}
                minScore={minScore}
                onMinScoreChange={setMinScore}
              />
            )}
          </main>
        ) : null}

        <footer className="footer">
          <p>{t(lang, 'footer_note')}</p>
        </footer>
      </div>
    </>
  )
}
