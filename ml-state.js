/* ml-state.js - tags MailerLite signups with the state page they came from.
   Reads <meta name="ps:state" content="Georgia"> and appends a hidden
   fields[state] input to every MailerLite form once the embed has rendered.
   MailerLite only stores the value if a custom field with key "state" exists
   in the account; if it does not, the field is simply ignored. */
(function () {
  var meta = document.querySelector('meta[name="ps:state"]');
  var state = meta && meta.content ? meta.content.trim() : '';
  if (!state) return;

  function tag() {
    var forms = document.querySelectorAll('.ml-embedded form');
    for (var i = 0; i < forms.length; i++) {
      var f = forms[i];
      if (f.querySelector('input[name="fields[state]"]')) continue;
      var input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'fields[state]';
      input.value = state;
      f.appendChild(input);
    }
  }

  tag();
  if (window.MutationObserver) {
    var mo = new MutationObserver(tag);
    mo.observe(document.documentElement, { childList: true, subtree: true });
    setTimeout(function () { mo.disconnect(); tag(); }, 15000);
  }
})();
