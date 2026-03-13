import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import enCommon from "./locales/en/common.json";
import zhCommon from "./locales/zh/common.json";

i18n.use(initReactI18next).init({
  resources: {
    en: { common: enCommon },
    zh: { common: zhCommon }
  },
  lng: "zh",
  fallbackLng: "en",
  interpolation: {
    escapeValue: false
  },
  defaultNS: "common"
});

export default i18n;
