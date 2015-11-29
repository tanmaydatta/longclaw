var knuth1 = angular.module('knuth');
knuth1.directive('onFinishRender', function($timeout) {
    return {
        restrict: 'A',
        link: function(scope, element, attr) {
            if (scope.$last === true) {
                $timeout(function() {
                    scope.$emit('ngRepeatFinished');
                });
            }
        }
    }
}).controller('album', ['$scope', '$http', '$window',
    function($scope, $http, $window) {

        $scope.aid = $window.hell;
        var aid = $scope.aid;
        var fb = "https://graph.facebook.com/v2.5/";
        var access = "CAACEdEose0cBAC57PdSuHcgme875LdubnEdrkaq4QvHsRZBooqrZAkDxjgR1G9Uxw4LJe9BAHivNij4lxAUZCZAJY2UWEKhuADOWoq5Vj2jaySdlcF0DvYxCFYD0fZBHC7mhyn6L7jKpgZAcJ77bUAbGFDSiNiOzvcHIZAZAtxINX7UioaW0OKSwHZCZCWfXn5UNqYpPCDstKwb2u7tRFE484r";
        $scope.accesstoken = access;
        var url = fb + aid + "/photos?access_token=" + access;
        $http.get(url)
            .then(function(response) {
                $scope.images = response.data.data;
                console.log($scope.images);


                angular.forEach($scope.images, function(value, key) {

                    console.log(value.id);
                    value.pic = fb + value.id + "/picture?access_token=" + access;

                });


            })

        $scope.$on('ngRepeatFinished', function(ngRepeatFinishedEvent) {
            //you also get the actual event object
            //do stuff, execute functions -- whatever...
            $(function() {

                // say we want to have only one item opened at one moment
                var opened = false;

                $('#repeat > div.uc-container').each(function(i) {
                    // alert("hello");
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
        });

    }
]);


$('#facebook').addClass('active item');








// $('.primary.button')
//   .api({    
//     url: '/facebook/'
//   })
// ;
