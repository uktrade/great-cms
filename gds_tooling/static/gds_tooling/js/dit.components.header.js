var dit = dit || {};
dit.components = dit.components || {};

dit.components.header = (new function() {
  var self = this;

  self.MENU_BUTTON = "#mobile-menu-button";
  self.MOBILE_NAV = "#great-header-mobile-nav";
  self.SEARCH_WRAPPER = "#great-header-search-wrapper";
  self.MENU_ITEMS_TAG = "js-menu-index";
  self.SUB_MENU_ITEMS_TAG = "js-sub-menu-index";
  self.MENU_ITEM_CONTAINER = "[data-js-menu-item-container]";
  self.SUB_MENU = "[data-js-sub-menu]";

  self.dataAttributeSelector = function(dataAttributeName) {
    return "[data-" + dataAttributeName + "]";
  };

  self.showButton = function() {
    $('#mobile-menu-button').addClass('ready');
  };

  self.toggleMenu = function() {
    var nav = $('#great-header-mobile-nav');
    var isCurrentlyExpanded = nav.attr('aria-expanded');

    if (isCurrentlyExpanded === 'true') {
      self.closeMenu();
    } else {
      self.openMenu();
    }
  };

  self.openMenu = function() {
    $(self.MENU_BUTTON).addClass('expanded').attr('aria-expanded', 'true');
    $(self.MOBILE_NAV).addClass('expanded').attr('aria-expanded', 'true');
    $(self.SEARCH_WRAPPER).addClass('hidden');

    self.moveFocusToMenuButton();
  };

  self.closeMenu = function() {
    $(self.MENU_BUTTON).removeClass('expanded').attr('aria-expanded', 'false');
    $(self.MOBILE_NAV).removeClass('expanded').attr('aria-expanded', 'false');
    $(self.SEARCH_WRAPPER).removeClass('hidden');

    self.moveFocusToMenuButton();
  };

  self.moveFocusToMenuButton = function() {
    $(self.MENU_BUTTON).focus();
  };

  self.getMenuItem = function(tag, index) {
    return $('[data-' + tag + '=' + index + ']');
  };

  self.getSubMenuItem = function(container, tag, index) {
    return container.find('[data-' + tag + '=' + index + ']').first();
  };

  self.moveFocusToFirstMenuItem = function() {
    self.getMenuItem(self.MENU_ITEMS_TAG, 0).focus();
  };

  self.moveFocusToSubMenu = function(target) {
    var mainMenuItemContainer = $(target).closest(self.MENU_ITEM_CONTAINER);
    mainMenuItemContainer.find(self.dataAttributeSelector(self.SUB_MENU_ITEMS_TAG)).first().focus();
  };

  self.moveFocusToMainMenu = function(target) {
    var mainMenuItemContainer = $(target).closest(self.MENU_ITEM_CONTAINER);
    var mainMenuItem = mainMenuItemContainer.find(self.dataAttributeSelector(self.MENU_ITEMS_TAG)).first();
    mainMenuItem.focus();
    return mainMenuItem;
  };

  self.moveFocusToPreviousMenuItem = function(target) {
    var currentIndex = parseInt($(target).data(self.MENU_ITEMS_TAG));
    if (currentIndex === 0) {
      self.closeMenu()
    } else {
      self.getMenuItem(self.MENU_ITEMS_TAG, currentIndex - 1).focus();
    }
  };

  self.moveFocusToPreviousSubMenuItem = function(target) {
    var currentIndex = parseInt($(target).data(self.SUB_MENU_ITEMS_TAG));
    if (currentIndex === 0) {
      self.moveFocusToMainMenu(target);
    } else {
      var subMenu = $(target).closest(self.SUB_MENU);
      self.getSubMenuItem(subMenu, self.SUB_MENU_ITEMS_TAG, currentIndex - 1).focus();
    }
  };

  self.moveFocusToNextMenuItem = function(target) {
    var currentIndex = parseInt($(target).data(self.MENU_ITEMS_TAG));
    var nextItem = self.getMenuItem(self.MENU_ITEMS_TAG, currentIndex + 1);
    if (nextItem.length) {
      nextItem.focus();
    } else {
      // at the end of the menu, loop back to the top
     self.moveFocusToFirstMenuItem();
    }
  };

  self.moveFocusToNextSubMenuItem = function(target) {
    var currentIndex = parseInt($(target).data(self.SUB_MENU_ITEMS_TAG));
    var subMenu = $(target).closest(self.SUB_MENU);
    var nextItem = self.getSubMenuItem(subMenu, self.SUB_MENU_ITEMS_TAG, currentIndex + 1);
    if (nextItem.length) {
      nextItem.focus();
    } else {
      // at the end of the sub menu, return to the next item in the main menu.
      var mainMenuItem = self.moveFocusToMainMenu(target);
      self.moveFocusToNextMenuItem(mainMenuItem);
    }
  };

  self.handleMenuButtonKeyDownEvents = function(event) {
      if (event.key === "Escape" || event.key === "ArrowUp" || event.key === "Esc" || event.key === "Up") {
        self.closeMenu();
        event.preventDefault();
      }
      if (event.key === "ArrowDown" || event.key === "Down") {
        self.openMenu();
        self.moveFocusToFirstMenuItem();
        event.preventDefault();
      }
  };

  self.handleMenuItemKeyDownEvents = function(event) {
    if (event.key === "Escape" || event.key === "Esc") {
      self.closeMenu();
      event.preventDefault();
    }
    if (event.key === "ArrowUp" || event.key === "Up") {
      self.moveFocusToPreviousMenuItem(event.target);
      event.preventDefault();
    }
    if (event.key === "ArrowDown" || event.key === "Down") {
      self.moveFocusToNextMenuItem(event.target);
      event.preventDefault();
    }
    if (event.key === "ArrowRight" || event.key === "Right") {
      self.moveFocusToSubMenu(event.target);
      event.preventDefault();
    }
  };

  self.handleSubMenuItemKeyDownEvents = function(event) {
    if (event.key === "Escape" || event.key === "Esc") {
      self.closeMenu();
      event.preventDefault();
    }
    if (event.key === "ArrowUp" || event.key === "Up") {
      self.moveFocusToPreviousSubMenuItem(event.target);
      event.preventDefault();
    }
    if (event.key === "ArrowDown" || event.key === "Down") {
      self.moveFocusToNextSubMenuItem(event.target);
      event.preventDefault();
    }
    if (event.key === "ArrowLeft" || event.key === "Left") {
      self.moveFocusToMainMenu(event.target);
      event.preventDefault();
    }
  };

  self.setupEventListeners = function() {
    $(self.MENU_BUTTON)
        .on("click", self.toggleMenu)
        .on("keydown", self.handleMenuButtonKeyDownEvents);

    $(self.dataAttributeSelector(self.MENU_ITEMS_TAG))
        .on("keydown", self.handleMenuItemKeyDownEvents);

    $(self.dataAttributeSelector(self.SUB_MENU_ITEMS_TAG))
        .on("keydown", self.handleSubMenuItemKeyDownEvents);
  };

  self.init = function() {
    self.setupEventListeners();

    // menu should start closed
    self.closeMenu();
    self.showButton();
  }
});

$(document).ready(function() {
  dit.components.header.init();
});
