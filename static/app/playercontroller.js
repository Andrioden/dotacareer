
app.controller('PlayerController', function($rootScope, $scope, $http, $modal){
    // IMPORTANT SCOPE VARIABLES
    $rootScope.player = undefined;

    // LOAD CURRENT PLAYER IF POSSIBLE
    $rootScope.player = null;
    $rootScope.loading_player = true;
    $http.get('/api/players/my').
        then(function(response) {
            if (response.data.has_player) {
                $rootScope.player = response.data.player;
            }
            $rootScope.loading_player = false;
        }, function(response) {
            AlertError(response);
            $rootScope.loading_player = false;
        });

    // EXPOSED ACTIONS FOR HTML
    $scope.submitPlayer = function() {
        $http.post('/api/players/register', {nick: $scope.register_nick}).
            then(function(response) {
                $scope.register_nick = "";
                $rootScope.player = response.data;
                console.log(response);
            }, function(response) {
                AlertError(response);
            });
    };

});
