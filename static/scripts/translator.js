var Cookie = {
    set: function (name, value, days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        var expires = "; expires=" + date.toUTCString();
        document.cookie = name + "=" + value + expires + "; path=/";
    },

    get: function (name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    },

    erase: function (name) {
        Cookie.set(name, "", -1);
    }
};

// Get current language from the cookie
function getCurrentLanguage() {
    var googtrans = Cookie.get('googtrans');
    if (googtrans) {
        var parts = googtrans.split('/');
        if (parts.length === 3) {
            return parts[2]; // Return the target language (e.g., 'mr' for Marathi)
        }
    }
    return 'en'; // Default to English if no cookie is found
}

// Set the current language in the dropdown
function setDropdownLanguageText(lang) {
    const languageDropdown = document.getElementById("languageDropdown");
    if (lang === "mr") {
        languageDropdown.innerText = "Marathi";
    } else if (lang === "hi") {
        languageDropdown.innerText = "Hindi";
    } else {
        languageDropdown.innerText = "English"; // Default to English
    }
}

// Initialize Google Translate
function googleTranslateElementInit() {
    new google.translate.TranslateElement({pageLanguage: 'en'}, 'translate');
}

document.addEventListener("DOMContentLoaded", function () {
    // Load Google Translate Script
    var googleTranslateScript = document.createElement("script");
    googleTranslateScript.type = "text/javascript";
    googleTranslateScript.async = true;
    googleTranslateScript.src = "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    (document.getElementsByTagName("head")[0] || document.getElementsByTagName("body")[0])
        .appendChild(googleTranslateScript);

    // Set current language in the dropdown
    var currentLang = getCurrentLanguage();
    setDropdownLanguageText(currentLang);

    // Event listener for language selection from dropdown
    document.querySelectorAll('.dropdown-item').forEach(function(item) {
        item.addEventListener('click', function () {
            var lang = this.getAttribute('data-lang');
            Cookie.set('googtrans', `/en/${lang}`, 7); // Set cookie for Google Translate
            Cookie.set('googtrans', `/auto/${lang}`, 7); // In case auto-detection is used
            window.location.reload(); // Reload page to apply translation
        });
    });
});
