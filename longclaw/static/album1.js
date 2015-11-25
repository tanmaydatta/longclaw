$('#facebook').addClass('active item');

$(function() {

    // say we want to have only one item opened at one moment
    var opened = false;

    $('#grid > div.uc-container').each(function(i) {

        var $item = $(this),
            direction;

        switch (i) {
            case 0:
                direction = ['right', 'bottom'];
                break;
            case 1:
                direction = ['left', 'bottom'];
                break;
            case 2:
                direction = ['right', 'top'];
                break;
            case 3:
                direction = ['left', 'top'];
                break;
        }

        var pfold = $item.pfold({
            folddirection: direction,
            speed: 300,
            onEndFolding: function() {
                opened = false;
            },
            centered: true
        });

        $item.find('span.icon-eye').on('click', function() {

            if (!opened) {
                opened = true;
                pfold.unfold();
            }

        }).end().find('span.icon-cancel').on('click', function() {

            pfold.fold();

        });

    });

});
