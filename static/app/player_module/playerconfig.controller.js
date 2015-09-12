app.controller('PlayerConfigDialogController', function ($rootScope, $scope, $modalInstance, $http) {
    // IMPORTANT CONTROLLER VARIABLES
    $scope.selectedConfigId = null;
    $scope.selectedConfig = null;

    // CONSTRUCTOR
    setActiveConfigAsSelectedConfig();

    $http.get('/api/heroes/rest/', {cache: true}).
        then(function(response) {
            $rootScope.heroes = response.data;
        }, function(response) {
            AlertError(response);
        });

    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.isCreatingNewConfig = false;
    $scope.createNewConfig = function() {
        $scope.isCreatingNewConfig = true;
        $http.post('/api/players/newConfig').
            then(function(response) {
                $rootScope.player.configs.push(response.data);
                $scope.selectedConfig = response.data;
                $scope.isCreatingNewConfig = false;
            }, function(response) {
                AlertError(response);
                $scope.isCreatingNewConfig = false;
            });
    }

    $scope.setSelectedConfig = function() {
        for(var i=0; i<$rootScope.player.configs.length; i++) {
            if ($rootScope.player.configs[i].id == $scope.selectedConfigId)
                $scope.selectedConfig = $rootScope.player.configs[i];
        }
    }

    $scope.isDoingConfigAction = false;

    $scope.updateSelectedConfig = function() {
        $scope.isDoingConfigAction = true;
        $http.post('/api/players/updateConfig', $scope.selectedConfig).
            then(function(response) {
                $scope.isDoingConfigAction = false;
            }, function(response) {
                AlertError(response);
                $scope.isDoingConfigAction = false;
            });
    }

    $scope.deleteSelectedConfig = function() {
        if (confirm("Are you sure you want to delete the config '" + $scope.selectedConfig.name + "'?")) {
            $scope.isDoingConfigAction = true;
            $http.post('/api/players/deleteConfig', {id: $scope.selectedConfig.id}).
                then(function(response) {
                    removeConfigFromConfigsList($scope.selectedConfig.id);
                    $scope.selectedConfig = null;
                    $scope.isDoingConfigAction = false;
                }, function(response) {
                    AlertError(response);
                    $scope.isDoingConfigAction = false;
                });
        }
    }

    $scope.setSelectedConfigAsActiveConfig = function() {
        $scope.isDoingConfigAction = true;
        $http.post('/api/players/setActiveConfig', {id: $scope.selectedConfig.id}).
            then(function(response) {
                deactivateAllConfigs();
                $scope.selectedConfig.active = true;
                $scope.isDoingConfigAction = false;
            }, function(response) {
                AlertError(response);
                $scope.isDoingConfigAction = false;
            });
    }

    $scope.removeHeroPriority = function(index) {
        $scope.selectedConfig.hero_priorities.splice(index,1);
    }

    $scope.addHeroPriority = function() {
        $scope.selectedConfig.hero_priorities.push({name: "", role: ""});
    }

    // PRIVATE FUNCTIONS
    function removeConfigFromConfigsList(id) {
        for(var i=0; i<$rootScope.player.configs.length; i++) {
            if ($rootScope.player.configs[i].id == id)
                $rootScope.player.configs.splice(i,1);
        }
    }

    function setActiveConfigAsSelectedConfig() {
        for(var i=0; i<$rootScope.player.configs.length; i++) {
            if ($rootScope.player.configs[i].active == true)
                $scope.selectedConfig = $rootScope.player.configs[i];
        }
    }

    function deactivateAllConfigs() {
        for(var i=0; i<$rootScope.player.configs.length; i++)
            $rootScope.player.configs[i].active = false;
    }

});