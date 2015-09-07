app.controller('PlayerController', function($rootScope, $scope, $http, $modal, WebSocketService){
    // IMPORTANT SCOPE VARIABLES
    $rootScope.player = undefined;

    // LISTEN TO EVENTS // EXPOSE METHODS TO OTHER CONTROLLERS
    WebSocketService.subscribe("NewPlayerDoingQueueCount", function(newMatchQueueCount){
        if ($rootScope.player.doing) $rootScope.player.doing.queued = newMatchQueueCount;
        $rootScope.$apply();
    });

    WebSocketService.subscribe("MatchCompleted", function(match){
        $rootScope.player.doing = null;
        $rootScope.$apply();
    });

    // LOAD CURRENT PLAYER IF POSSIBLE
    $rootScope.player = null;
    $rootScope.loadingPlayer = true;
    $http.get('/api/players/my').
        then(function(response) {
            if (response.data.has_player) {
                $rootScope.player = response.data.player;
                GLOBAL_VAR_LOL = $rootScope.player
            }
            $rootScope.loadingPlayer = false;
        }, function(response) {
            AlertError(response);
            $rootScope.loadingPlayer = false;
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

    $scope.isDoingRelatedAjaxRunning = false;

    $scope.playAgainstBots = function() {
        $scope.isDoingRelatedAjaxRunning = true;
        $http.post('/api/matches/playAgainstBots').
            then(function(response) {
                matchWasPlayed(response.data.match);
                $scope.isDoingRelatedAjaxRunning = false;
            }, function(response) {
                AlertError(response);
                $scope.isDoingRelatedAjaxRunning = false;
            });
    }

    $scope.joinSoloMatchQueue = function(type) {
        $scope.isDoingRelatedAjaxRunning = true;
        $http.post('/api/matches/joinSoloQueue', {type: type}).
            then(function(response) {
                $rootScope.player.doing = response.data.doing;
                if (response.data.match) matchWasPlayed(response.data.match);
                $scope.isDoingRelatedAjaxRunning = false;
            }, function(response) {
                AlertError(response);
                $scope.isDoingRelatedAjaxRunning = false;
            });
    }

    $scope.stopDoing = function() {
        $scope.isDoingRelatedAjaxRunning = true;
        $http.post('/api/players/stopDoing').
            then(function(response) {
                $rootScope.player.doing = null;
                $scope.isDoingRelatedAjaxRunning = false;
            }, function(response) {
                AlertError(response);
                $scope.isDoingRelatedAjaxRunning = false;
            });
    }

    $scope.openPlayerConfigDialog = function() {
        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'playerConfigDialog.html',
            controller: 'PlayerConfigDialogController',
        });
    }

    // PRIVATE FUNCTIONS

    function matchWasPlayed(match) {
        $rootScope.player.matches.push(match);
        $rootScope.$broadcast('MatchesControllerEvent_OpenMatchDialog', match);
    }

});