/* GENERATED — kit/build-tokens.mjs: language.json + themes/default.json. Không sửa tay. */
window.KIT_TOKENS = {
 "_generated": "kit/build-tokens.mjs: language.json + themes/default.json. Không sửa tay.",
 "theme": "default",
 "canvas": {
  "w": 1080,
  "h": 1920,
  "fps": 30
 },
 "colors": {
  "surface": "#ffffff",
  "accent_dark": "#1664ba",
  "accent_primary": "#1872ce",
  "accent_mid": "#3e9cec",
  "accent_light": "#8ec8f6",
  "ink": "#010102",
  "ink_secondary": "#383a3b",
  "yellow": "#fcc435"
 },
 "page": {
  "tint": "#eef7fc",
  "white": "#ffffff",
  "tint_share": [
   0.536,
   0.925
  ],
  "white_share": [
   0.075,
   0.464
  ],
  "grid": {
   "line": {
    "pitch_px": 180,
    "contrast_lum": 23.2
   },
   "dot": {
    "pitch_px": 46,
    "contrast_lum": 10.6
   }
  }
 },
 "font": {
  "family": "Be Vietnam Pro",
  "body_weight": 700
 },
 "type": {
  "headline": {
   "px": 84,
   "weight": 800,
   "range_px": [
    60,
    105
   ]
  },
  "subhead": {
   "px": 56,
   "weight": 700,
   "range_px": [
    36,
    87
   ]
  },
  "caption": {
   "px": 80,
   "weight": 800,
   "range_px": [
    64,
    124
   ]
  },
  "list_item": {
   "px": 50,
   "weight": 800,
   "range_px": [
    37,
    66
   ]
  },
  "pill_label": {
   "px": 40,
   "weight": 800,
   "range_px": [
    32,
    43
   ]
  },
  "display_number": {
   "px": 154,
   "weight": 800,
   "range_px": [
    118,
    302
   ]
  },
  "percent_label": {
   "px": 90,
   "weight": 800,
   "range_px": [
    56,
    115
   ]
  },
  "line_height": 1.03,
  "letter_spacing_em": 0,
  "label_letter_spacing_em": 0,
  "case": {
   "headline": "none",
   "label": "none"
  },
  "highlight": {
   "style": "color",
   "marker_alpha": 0
  }
 },
 "card": {
  "radius": 24,
  "shadow": "0 13px 53px rgba(21,101,192,0.18)",
  "width_px": 731,
  "padding": {
   "left": 113,
   "right": 82,
   "top": 29,
   "bottom": 75
  }
 },
 "pill": {
  "radius": 41,
  "shadow": "0 10px 40px rgba(21,101,192,0.19)",
  "width_px": 470,
  "height_px": 83,
  "padding": {
   "left": 12,
   "right": 24,
   "top": 19,
   "bottom": 17
  }
 },
 "iso": [
  "#aad5fa",
  "#90c7f3",
  "#1b74d0"
 ],
 "safe": {
  "box": [
   143,
   290,
   874,
   1415
  ],
  "reserved_bottom_frac_H": 0.263
 },
 "motion": {
  "card_slide_in": {
   "ease": "power2.out",
   "reach_s": 0.475,
   "settle_s": 0.475,
   "overshoot": 0,
   "distance_frac": 0.327,
   "distance_of": "H"
  },
  "number_count_up": {
   "ease": "sine.out",
   "reach_s": 0.767,
   "settle_s": 0.933,
   "overshoot": 0,
   "distance_frac": 0.531,
   "distance_of": "W"
  },
  "bar_fill": {
   "ease": "power1.inOut",
   "reach_s": 0.683,
   "settle_s": 0.683,
   "overshoot": 0,
   "distance_frac": 0.487,
   "distance_of": "W"
  },
  "chart_pop": {
   "ease": "back.out(2.5)",
   "reach_s": 0.117,
   "settle_s": 0.433,
   "overshoot": 0.181,
   "distance_frac": 0.097,
   "distance_of": "H",
   "stagger_s": [
    0.167,
    0.133
   ]
  },
  "pill_progress": {
   "hop_frames": 1,
   "pop_scale": 1.08,
   "settle_s": 0.033
  },
  "typed_text": {
   "chars_per_s": 21.3,
   "chars_per_s_range": [
    20.4,
    22.2
   ]
  },
  "button_pulse": {
   "ease": "power1.in",
   "reach_s": 1.4,
   "scale": 1.175,
   "scale_source": "preset.md (bảng Primitive, button_swell_pre_click)",
   "release_ease": "expo.out",
   "release_s": 0.067
  }
 },
 "transitions": {
  "bar-wipe": {
   "duration_s": 0.333,
   "share": 0.167
  },
  "dissolve": {
   "duration_s": 0.333,
   "share": 0.333
  },
  "flash-wipe": {
   "duration_s": 0.333,
   "share": 0.067
  },
  "hard": {
   "duration_s": 0.033,
   "share": 0.2
  },
  "wash": {
   "duration_s": 0.233,
   "share": 0.233
  }
 },
 "rhythm": {
  "text_dwell_median_s": 2.01,
  "text_dwell_range_s": [
   1.67,
   5.25
  ],
  "hold_median_s": 0.83,
  "shot_len_median_s": 4.77,
  "shot_len_p10_p90_s": [
   2.43,
   8.17
  ],
  "bursts_per_min": 29.95,
  "burst_len_median_s": 0.355
 },
 "guess": {
  "fade_up": {
   "y_px": 28,
   "duration_s": 0.35,
   "ease": "power2.out",
   "note": "style.json không có token vào cảnh cho tiêu đề/caption; mượn họ ease card_slide_in"
  }
 },
 "catalog": {
  "component": [
   "page",
   "card",
   "text",
   "accentBar",
   "icon",
   "avatar",
   "progressBar",
   "barChart",
   "lineChart",
   "donutChart",
   "skeleton",
   "kpi",
   "button",
   "pill",
   "dashboardCard",
   "statCard",
   "quoteCard",
   "mapCard",
   "iconCard",
   "listCard",
   "stepCard",
   "connector",
   "table",
   "chatBox"
  ],
  "effect": [
   "fadeUp",
   "slideIn",
   "typing",
   "countUp",
   "barFill",
   "chartPop",
   "popIn",
   "ringFill",
   "pulse",
   "pillHop"
  ],
  "transition": [
   "dissolve",
   "wash",
   "hard",
   "bar-wipe",
   "flash"
  ]
 }
};
