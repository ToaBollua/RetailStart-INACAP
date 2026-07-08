<?php
// H0P3 Custom Adminer Definition v4.0 — Permanent Session Bypass
// Usa permanentLogin() para forzar autenticación sin cookie ni POST.

class AdminerAutologin extends \Adminer\Adminer {

    function credentials() {
        // Credenciales hardcodeadas — sin formulario, sin input humano.
        return array('srv-db-postgres-primary', 'retail_user', 'retail_pass');
    }

    function database() {
        return 'retail_dw';
    }

    function login($login, $password) {
        // Acepta cualquier intento — la validación real ya está en credentials()
        return true;
    }

    function permanentLogin($create = false) {
        // Clave estática → Adminer la acepta como token de sesión permanente válido.
        // Esto elimina la necesidad de POST falso o cookies de sesión.
        return 'h0p3_retail_permanent_token_2026';
    }

    function headers() {
        // Elimina restricciones de enmarcado para permitir iframe desde el dashboard
        header_remove("X-Frame-Options");
        header("X-Frame-Options: ALLOWALL");
        header("Content-Security-Policy: frame-ancestors 'self' http://localhost:8083 http://127.0.0.1:8083;");
        return true;
    }
}

return new AdminerAutologin();
