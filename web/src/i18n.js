export const LANG_KEY = 'pokopia-planner-lang'

export const I18N = {
  en: {
    mode1_num: 'Mode 1',
    mode1_title: 'Pokémon → Items',
    mode2_num: 'Mode 2',
    mode2_title: 'Coming soon',
    mode1_lede:
      'Pick the Pokémon you want to house together. We’ll rank items that match their favorites, and warn you when Ideal Habitats clash.',
    picker_heading: 'Choose Pokémon',
    results_heading: 'Suggested items',
    search_placeholder: 'Search by name, habitat, or favorite…',
    clear: 'Clear',
    min_score: 'Min matches',
    results_empty: 'Select at least one Pokémon to see ranked items.',
    results_filtered:
      'No items reach the minimum match count. Try lowering the filter.',
    score_label: 'matches',
    liked_by: 'Liked by',
    warning_title: 'Ideal Habitat conflict',
    warning_intro:
      'These Pokémon prefer opposite conditions in the same living area:',
    footer_note:
      'Fan tool for Pokémon Pokopia. Unofficial — not affiliated with Nintendo, The Pokémon Company, or Game Freak.',
    vs: 'vs',
    lang_label: 'Language',
    load_error:
      'Could not load planner data. Serve the built site over HTTP (GitHub Pages or a local static server).',
  },
  ja: {
    mode1_num: 'モード1',
    mode1_title: 'ポケモン → アイテム',
    mode2_num: 'モード2',
    mode2_title: '近日公開',
    mode1_lede:
      '同じ場所に住ませたいポケモンを選ぶと、好みに合うアイテムを優先度つきで表示します。理想の環境がぶつかる場合は警告します。',
    picker_heading: 'ポケモンを選ぶ',
    results_heading: 'おすすめアイテム',
    search_placeholder: '名前・環境・好みで検索…',
    clear: 'クリア',
    min_score: '最低一致数',
    results_empty: 'ポケモンを選ぶと、ランキングが表示されます。',
    results_filtered:
      '最低一致数に達するアイテムがありません。フィルターを下げてみてください。',
    score_label: '一致',
    liked_by: '好きなポケモン',
    warning_title: '理想の環境の衝突',
    warning_intro: '同じ場所で正反対の環境を好むポケモンがいます：',
    footer_note:
      '『Pokémon Pokopia』のファン向けツールです。任天堂・ポケモン・ゲームフリーク公式ではありません。',
    vs: '対',
    lang_label: '言語',
    load_error:
      'プランナーデータを読み込めませんでした。HTTP 経由でサイトを開いてください。',
  },
  zh_tw: {
    mode1_num: '模式 1',
    mode1_title: '寶可夢 → 道具',
    mode2_num: '模式 2',
    mode2_title: '即將推出',
    mode1_lede:
      '選擇想放在同一生活區的寶可夢，依喜好排出適合的道具；若理想環境互相衝突會顯示警告。',
    picker_heading: '選擇寶可夢',
    results_heading: '推薦道具',
    search_placeholder: '依名稱、環境或喜好搜尋…',
    clear: '清除',
    min_score: '最低相符數',
    results_empty: '請先選擇至少一隻寶可夢。',
    results_filtered: '沒有達到最低相符數的道具，請調低篩選條件。',
    score_label: '相符',
    liked_by: '喜歡的寶可夢',
    warning_title: '理想環境衝突',
    warning_intro: '這些寶可夢在同一生活區偏好相反的環境：',
    footer_note:
      '寶可夢 Pokopia 粉絲工具。非官方，與任天堂、寶可夢公司或 Game Freak 無關。',
    vs: '對',
    lang_label: '語言',
    load_error: '無法載入規劃資料。請透過 HTTP（GitHub Pages 或本機伺服器）開啟。',
  },
}

export function t(lang, key) {
  return I18N[lang]?.[key] ?? I18N.en[key] ?? key
}

export function htmlLang(lang) {
  if (lang === 'zh_tw') return 'zh-Hant'
  if (lang === 'ja') return 'ja'
  return 'en'
}

export function assetUrl(relativePath) {
  const base = import.meta.env.BASE_URL || './'
  return `${base}${relativePath.replace(/^\//, '')}`
}
