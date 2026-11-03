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
  "yellow": "#fcc435",
  "mark": "#fcc435"
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
  "body_weight": 700,
  "accent_family": "Newsreader"
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
  },
  "accent_italic": {
   "size_ratio": 1.27,
   "weight": 500
  },
  "outline": {
   "stroke_em": 0.037
  },
  "strike": {
   "thick_em": 0.064,
   "line_cy_over_cap_h": 0.5,
   "cap_h_em": 0.74,
   "baseline_em": 0.88,
   "overshoot": 0.06,
   "dim": {
    "opacity": 0.84,
    "grayscale": 1,
    "basis": "chữ bị gạch chuyển về xám: đen #242424 -> #404040 và xanh nhấn #1872ce -> #797979; cùng một hệ số khi coi là grayscale + opacity trên nền sáng ~#e8f0fc: 0.857 và 0.82, lấy 0.84"
   }
  },
  "mark": {
   "alpha": 0.86,
   "top": 0.356,
   "bottom": 0.822
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
  },
  "tab_switch": {
   "source": "jobs/corp-sample-7700229527049358612/instances.json (tabs_cursor), measure_tabs_cursor.py + fit_back_edges.py; n=2 chuyển tab trong 1 clip (clip 7700229527049358612), thấy bằng mắt ở 3 clip mới",
   "lead_edge": {
    "ease": "back.out(1.35)",
    "dur_s": 0.217,
    "overshoot": 0.06,
    "note": "cạnh dẫn (phía đang tới) của pill chạy trước, quá đà ~6% quãng; đo cạnh phải khi đi sang phải"
   },
   "trail_edge": {
    "ease": "power1.out",
    "reach_s": 0.417,
    "note": "cạnh theo sau đến muộn: pill giãn dài ra giữa chuyển động (rộng ~1.4-1.55x lúc đỉnh) rồi co về"
   }
  },
  "cursor_glide": {
   "source": "jobs/corp-sample-7700229527049358612/instances.json (tabs_cursor), measure_tabs_cursor.py + fit_back_edges.py; n=2 chuyển tab trong 1 clip (clip 7700229527049358612), thấy bằng mắt ở 3 clip mới",
   "ease": "power2.inOut",
   "reach_s": 0.367,
   "duration_independent_of_distance": true,
   "distance_px_measured": [
    599,
    246
   ],
   "origin_offset_px": [
    294,
    522
   ],
   "origin_note": "điểm thấy đầu tiên của con trỏ so với đích (clip đo: vào từ dưới phải); lần lướt thứ hai bắt đầu từ chỗ cũ",
   "click_lag_s": 0.017,
   "click_note": "pill bắt đầu chạy đúng lúc con trỏ tới (0 và 1 khung sau)"
  },
  "strike": {
   "source": "jobs/corp-sample-7701337835403726101/strike.json; n=2 thể hiện cùng một clip",
   "ease": "expo.out",
   "reach_s": 0.148,
   "dim_delay_frames": 1,
   "fit": "expo.out khớp rmse 0.0035 ('101', D 9.0 khung) và 0.017 ('CÁI SAI.', D 6.75 khung); chạm 98% sau 3.8 đến 5.1 khung, lấy 4.45 = 0.148s",
   "progress_first_frames": [
    [
     0,
     0.226,
     0.649,
     0.845,
     0.921,
     0.966,
     0.989
    ],
    [
     0,
     0.005,
     0.68,
     0.854,
     0.927,
     0.963,
     0.982
    ]
   ],
   "dim_note": "chữ chuyển xám sau vạch 1 khung (khung vạch bắt đầu hiện còn nguyên màu)"
  },
  "mark": {
   "source": "jobs/corp-sample-7700960427491986696/mark.json; n=2 thể hiện, 2 clip (7700960427491986696, 7702043938013629716)",
   "ease": "expo.out",
   "reach_s": 0.164,
   "fit": "expo.out khớp rmse 0.0046 (D 7.75 khung) và 0.0040 (D 9.75 khung); chạm 98% sau 4.4 đến 5.5 khung, lấy 4.93 = 0.164s; quét trái -> phải",
   "progress_first_frames": [
    [
     0,
     0.154,
     0.658,
     0.862,
     0.93,
     0.98,
     0.993
    ],
    [
     0,
     0.473,
     0.736,
     0.868,
     0.934,
     0.967,
     0.989
    ]
   ]
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
  },
  "tab_label_swap": {
   "at_frac_of_lead_dur": 0.5,
   "note": "đổi màu nhãn tab (tối <-> trắng) ở giữa lúc cạnh dẫn chạy; chưa đo"
  }
 },
 "tabs": {
  "source": "jobs/corp-sample-7700229527049358612/instances.json (tabs_cursor), measure_tabs_cursor.py + fit_back_edges.py; n=2 chuyển tab trong 1 clip (clip 7700229527049358612), thấy bằng mắt ở 3 clip mới",
  "strip_h_px": 78,
  "pill_h_px": 68,
  "pitch_px": 247,
  "pill_inset_px": 10,
  "label_cap_px": 20,
  "label_scale_of_pill_label": 0.72,
  "cursor": {
   "w_px": 37,
   "h_px": 50,
   "tip_dx_frac_pitch": 0.198,
   "tip_dy_px_from_strip_top": 64
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
   "chatBox",
   "tabs"
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
   "pillHop",
   "tabSwitch",
   "strike",
   "mark"
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
