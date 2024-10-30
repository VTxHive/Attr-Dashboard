// base.js

// Get the menu button and menu elements
const menuBtn = document.getElementById('menu-btn');
const menu = document.getElementById('menu');

// Add event listener to the menu button
menuBtn.addEventListener('click', () => {
    menu.classList.toggle('show');
});