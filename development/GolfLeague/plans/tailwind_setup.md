# Tailwind Configuration Plan

## Masters Theme Implementation

The following Tailwind configuration must be created to support the new UI in `templates/new/`:

```js
tailwind.config.js;
module.exports = {
  content: ["./templates/new/**/*.html"],
  theme: {
    extend: {
      colors: {
        masters: {
          green: "#076652",
          "green-dark": "#0A3F36",
          "green-light": "#2E5A52",
          gold: "#D4AF37",
          "gold-dark": "#C9A227",
          offwhite: "#F8F9F6",
          charcoal: "#1C2C2A",
        },
      },
      borderRadius: {
        "2xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
```

## Critical Notes

- Configuration must **only** target `templates/new/` to avoid affecting existing UI
- No changes to existing templates or backend logic
- This file will be created during Code mode implementation
