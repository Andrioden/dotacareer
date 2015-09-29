app.controller('PlayerController', function($rootScope, $scope, $http, $modal, WebSocketService){
    // IMPORTANT SCOPE VARIABLES
    $rootScope.player = undefined;

    // LISTEN TO EVENTS // EXPOSE METHODS TO OTHER CONTROLLERS
    WebSocketService.subscribe("Match_NewQueueCount", function(newMatchQueueCount){
        if ($rootScope.player.doing) $rootScope.player.doing.queued = newMatchQueueCount;
        $rootScope.$apply();
    });
    WebSocketService.subscribe("Match_Finished", function(match){
        $rootScope.player.doing = null;
        $rootScope.$apply();
    });
    WebSocketService.subscribe("Player_MatchFound", function(match){
        $rootScope.player.doing = match;
        $rootScope.$apply();
    });
    WebSocketService.subscribe("Player_CashChange", function(payout){
        $rootScope.player.cash += payout;
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
            $rootScope.register_player_form_data = response.data.register_player_form_data
        }, function(response) {
            alertError(response);
            $rootScope.loadingPlayer = false;
        });

    // EXPOSED ACTIONS FOR HTML
    $scope.submitPlayer = function() {
        if($scope.selectedPlayerClass == null)
        {
            $scope.selectedPlayerClassError = "Mandatory";
            return;
        }

        $http.post('/api/players/register', {nick: $scope.register_nick, player_class: $scope.selectedPlayerClass}).
            then(function(response) {
                $rootScope.player = response.data;
            }, function(response) {
                alertError(response);
            });
    };

    $scope.setSelectedPlayerClass = function(selectedPlayerClass) {
        $scope.selectedPlayerClass = selectedPlayerClass;
    };

    $scope.isDoingRelatedAjaxRunning = false;

    $scope.playAgainstBots = function() {
        $scope.isDoingRelatedAjaxRunning = true;
        $http.post('/api/matches/playAgainstBots').
            then(function(response) {
                $rootScope.player.doing = response.data;
                $rootScope.player.matches.push(response.data);
                $rootScope.$broadcast('MatchesControllerEvent_OpenMatchDialog', response.data);
                $scope.isDoingRelatedAjaxRunning = false;
            }, function(response) {
                alertError(response);
                $scope.isDoingRelatedAjaxRunning = false;
            });
    }

    $scope.joinSoloMatchQueue = function(type) {
        $scope.isDoingRelatedAjaxRunning = true;
        $http.post('/api/matches/joinSoloQueue', {type: type}).
            then(function(response) {
                $rootScope.player.doing = response.data.doing;
                $scope.isDoingRelatedAjaxRunning = false;
            }, function(response) {
                alertError(response);
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
                alertError(response);
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

    // PRIVATE METHODS

});