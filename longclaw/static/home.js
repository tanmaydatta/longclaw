$('#home').addClass('active item');
$('.menu .item')
    .tab();
// $('.infinite.aa.demo.segment')
//     .visibility({
//         once: false,
//         // update size when new content loads
//         observeChanges: true,
//         // load content on bottom edge visible
//         onBottomVisible: function() {
//             // loads a max of 5 times
//             window.loadFakeContent();
//         }
//     });

$('.ui.sticky')
    .sticky({
        context: '#aa'
    });
