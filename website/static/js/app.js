$(function () {

    window.sr = ScrollReveal();

    sr.reveal('.js--fadeInRight', {
        origin: 'right',
        distance: '300px',
        easing: 'ease-in-out',
        duration: 800,
        mobile: false,
    });


});

const tricks = document.getElementById('tricks');
const about = document.getElementById('about')
const dict = document.getElementById('dict')

tricks.addEventListener('mouseenter', e => {
    console.log(e);
})