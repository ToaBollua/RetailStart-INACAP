<?php
// H0P3 Adminer Entrypoint v4.0 — Limpio, sin hacks de POST
// El autologin lo gestiona permanentLogin() en my_custom_adminer.php

namespace docker {
    function adminer_object() {
        return include "./my_custom_adminer.php";
    }
}

namespace {
    // Servir el CSS custom cuando Adminer lo solicita
    if (basename($_SERVER['DOCUMENT_URI'] ?? $_SERVER['REQUEST_URI']) === 'adminer.css' && is_readable('adminer.css')) {
        header('Content-Type: text/css');
        readfile('adminer.css');
        exit;
    }

    function adminer_object() {
        return \docker\adminer_object();
    }

    require('adminer.php');
}
