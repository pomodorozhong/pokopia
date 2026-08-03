import { assetUrl, t } from '../i18n'
import {
  favoriteLabel,
  itemCategory,
  itemLabel,
  localizeName,
} from '../lib/labels'
import { rankItems } from '../lib/ranking'

function ItemCard({ row, data, lang, index }) {
  return (
    <article
      className="item-card"
      style={{ animationDelay: `${Math.min(index, 12) * 20}ms` }}
    >
      <img
        src={assetUrl(`icons/items/${row.slug}.png`)}
        alt=""
        loading="lazy"
        onError={(e) => {
          e.currentTarget.style.opacity = '0.25'
        }}
      />
      <div>
        <h3 className="item-name">{itemLabel(data, row.slug, lang)}</h3>
        <p className="item-cat">{itemCategory(data, row.slug, lang)}</p>
        <div className="tag-row">
          {row.matchedFavorites.map((f) => (
            <span key={f} className="tag">
              {favoriteLabel(data, f, lang)}
            </span>
          ))}
        </div>
        <div className="beneficiaries" aria-label={t(lang, 'liked_by')}>
          {row.benefiting.map((p) => {
            const name = localizeName(p.names, lang, p.name_en)
            return (
              <img
                key={p.name_en}
                src={assetUrl(`icons/pokemon/${p.icon}.png`)}
                alt={name}
                title={name}
                loading="lazy"
              />
            )
          })}
        </div>
      </div>
      <div className="score-box">
        <span className="score">{row.criteriaScore}</span>
        <span className="score-label">{t(lang, 'score_label')}</span>
      </div>
    </article>
  )
}

export default function ResultsPanel({
  data,
  lang,
  selected,
  minScore,
  onMinScoreChange,
}) {
  const selectedPokemon = data.pokemon.filter((p) => selected.has(p.name_en))
  const ranked = rankItems(selectedPokemon, data.favorite_items)
  const filtered = ranked.filter((r) => r.criteriaScore >= minScore)

  let hint = null
  if (!selectedPokemon.length) {
    hint = t(lang, 'results_empty')
  } else if (!filtered.length) {
    hint = t(lang, 'results_filtered')
  }

  return (
    <section className="panel results-panel" aria-labelledby="results-heading">
      <div className="panel-head">
        <h2 id="results-heading">{t(lang, 'results_heading')}</h2>
        <div className="results-meta">
          <label className="filter-label">
            <span>{t(lang, 'min_score')}</span>
            <select
              className="min-score"
              value={minScore}
              onChange={(e) => onMinScoreChange(Number(e.target.value) || 1)}
            >
              <option value={1}>1+</option>
              <option value={2}>2+</option>
              <option value={3}>3+</option>
              <option value={4}>4+</option>
            </select>
          </label>
          <span className="count-pill">{filtered.length}</span>
        </div>
      </div>

      {hint ? <p className="results-hint">{hint}</p> : null}

      <div className="results-list">
        {filtered.map((row, index) => (
          <ItemCard
            key={row.slug}
            row={row}
            data={data}
            lang={lang}
            index={index}
          />
        ))}
      </div>
    </section>
  )
}
