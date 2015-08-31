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
                GLOBAL_VAR_LOL = $rootScope.player
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

    $scope.isJoiningOrBotting = false;

    $scope.playAgainstBots = function() {
        $scope.isJoiningOrBotting = true;
        $http.post('/api/matches/playAgainstBots').
            then(function(response) {
                //$rootScope.player.doing = response.data;
                $rootScope.player.matches.push(response.data.match);
                $rootScope.$broadcast('MatchesControllerEvent_OpenMatchDialog', response.data.match);
                $scope.isJoiningOrBotting = false;
            }, function(response) {
                AlertError(response);
                $scope.isJoiningOrBotting = false;
            });
    }

    $scope.joinSoloMatchQueue = function(type) {
        $scope.isJoiningOrBotting = true;
        $http.post('/api/matches/joinSoloQueue', {type: type}).
            then(function(response) {
                $rootScope.player.doing = response.data;
                $scope.isJoiningOrBotting = false;
            }, function(response) {
                AlertError(response);
                $scope.isJoiningOrBotting = false;
            });
    }

    $scope.stopDoing = function() {
        $http.post('/api/players/stopDoing').
            then(function(response) {
                $rootScope.player.doing = null;
            }, function(response) {
                AlertError(response);
            });
    }

});
