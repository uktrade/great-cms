
var DIT_SHARED = {};

DIT_SHARED.header = {
    init: function() {
        var sharedHeader = document.querySelector('.shared-header');
        var menuButton = sharedHeader.querySelector('button');
        var menu = sharedHeader.querySelector('.menu');
        var isMenuOpen = false;

        menu.style.display = 'none';

        menuButton.addEventListener('click', function(e) {
            e.preventDefault();
            menu.style.display = isMenuOpen ? 'none' : 'block';
            isMenuOpen = !isMenuOpen;
        });
    }
}
