import { t } from '../i18n'
import { habitatLabel, localizeName } from '../lib/labels'

export default function HabitatWarning({ conflicts, data, lang }) {
  if (!conflicts.length) return null

  return (
    <div className="habitat-warning" role="alert">
      <strong>{t(lang, 'warning_title')}</strong>
      <div>{t(lang, 'warning_intro')}</div>
      <ul>
        {conflicts.map((c) => {
          const leftNames = c.left
            .map((p) => localizeName(p.names, lang, p.name_en))
            .join(', ')
          const rightNames = c.right
            .map((p) => localizeName(p.names, lang, p.name_en))
            .join(', ')
          return (
            <li key={`${c.pair[0]}-${c.pair[1]}`}>
              <strong>{habitatLabel(data, c.pair[0], lang)}</strong> ({leftNames}){' '}
              {t(lang, 'vs')}{' '}
              <strong>{habitatLabel(data, c.pair[1], lang)}</strong> ({rightNames})
            </li>
          )
        })}
      </ul>
    </div>
  )
}
