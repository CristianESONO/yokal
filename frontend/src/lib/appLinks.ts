// Liens vers l'application Django (login / inscription).
// L'URL de base est configurable via NEXT_PUBLIC_APP_URL :
//   - en local  : http://localhost:8000
//   - en prod   : l'URL du VPS (ex. https://app.yokalma.com)
// Valeur par défaut = localhost pour le dev.
const APP_URL = process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:8000";

export const LOGIN_URL = `${APP_URL}/accounts/login/`;
export const REGISTER_URL = `${APP_URL}/accounts/register/`;
