app.controller('PlayerConfigDialogController', function ($rootScope, $scope, $modalInstance, $http, $timeout) {
    // IMPORTANT CONTROLLER VARIABLES
    $scope._selectedConfigIdTempStorage = null; // Only used as the ng-model the config selector should point to, should not be used.
    $scope.selectedConfig = null;
    $scope.heroes = [];

    // CONSTRUCTOR
    setActiveConfigAsSelectedConfig();
    // Timeout needed to redraw the sliders because of limitations of the slider plugin (https://github.com/rzajac/angularjs-slider/issues/79)
    $timeout(function () {
        $scope.$broadcast('rzSliderForceRender');
    });

    $http.get('/api/heroes/rest/', {cache: true}).
        then(function(response) {
            $scope.heroes = response.data;
            addPlayerHeroStatsData($scope.heroes);
        }, function(response) {
            alertError(response);
        });

    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.isAddingConfig = false;

    $scope.addConfig = function() {
        $scope.isAddingConfig = true;
        $http.post('/api/players/addConfig').
            then(function(response) {
                $rootScope.player.configs.push(response.data);
                $scope.selectedConfig = response.data;
                $scope.isAddingConfig = false;
            }, function(response) {
                alertError(response);
                $scope.isAddingConfig = false;
            });
    }

    $scope.setSelectedConfigIdAsSelectedConfig = function() {
        for(var i=0; i<$rootScope.player.configs.length; i++) {
            if ($rootScope.player.configs[i].id == $scope._selectedConfigIdTempStorage) {
                $scope.selectedConfig = $rootScope.player.configs[i];
                $scope._selectedConfigIdTempStorage = null; // Just to make it 100% clear that this variable should not be used
                return;
            }
        }
    }

    $scope.translateTrollLevelToText = function(value) {
        if (value == null) return "None";
        else if (typeof value  !== "undefined") return ["None", "Derp", "Much Troll", "Attempt at master trolling"][value];
    }

    $scope.translateFlameLevelToText = function(value) {
        if (value == null) return "None";
        else if (typeof value  !== "undefined") return ["None", "Mental poking", "Leave no fault uncommented", "Rager"][value];
    }

    $scope.isDoingConfigAction = false;

    $scope.updateSelectedConfig = function() {
        $scope.isDoingConfigAction = true;
        $http.post('/api/players/updateConfig', $scope.selectedConfig).
            then(function(response) {
                $scope.isDoingConfigAction = false;
            }, function(response) {
                alertError(response);
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
                    alertError(response);
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
                alertError(response);
                $scope.isDoingConfigAction = false;
            });
    }

    $scope.removeHeroPriority = function(index) {
        $scope.selectedConfig.hero_priorities.splice(index,1);
    }

    $scope.addHeroPriority = function() {
        $scope.selectedConfig.hero_priorities.push({name: "", role: ""});
    }

    $scope.getHeroPriorityRowRoleStat = function(index, role) {
        var heroName = $scope.selectedConfig.hero_priorities[index].name;
        for (var i=0; i<$scope.heroes.length; i++) {
            if ($scope.heroes[i].name == heroName) {
                if ($scope.heroes[i].playerStats) {
                    if ($scope.heroes[i].playerStats.stats[role] == 0)
                        return "";
                    else if ($scope.heroes[i].playerStats.stats[role] > 0)
                        return " (+" + $scope.heroes[i].playerStats.stats[role] + ")";
                    else
                        return " (" + $scope.heroes[i].playerStats.stats[role] + ")";
                }
                else return "";
            }
        }
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

    function addPlayerHeroStatsData(heroes) {
        for (var i=0; i<heroes.length; i++) {
            heroes[i].displayName = heroes[i].name;
            for(var y=0; y<$rootScope.player.hero_stats.length; y++) {
                if ($rootScope.player.hero_stats[y].hero == heroes[i].name) {
                    heroes[i].playerStats = $rootScope.player.hero_stats[y];
                    var statOverall = $rootScope.player.hero_stats[y].stats.overall;
                    if (statOverall > 0) heroes[i].displayName = heroes[i].name + " (+" + statOverall + ")";
                    else if (statOverall < 0) heroes[i].displayName = heroes[i].name + " (" + statOverall + ")";
                }
            }
        }
        // Sort by stats.overall
        heroes.sort(function(a, b){
            var aOverall = 0;
            var bOverall = 0;
            if (a.playerStats) aOverall = a.playerStats.stats.overall;
            if (b.playerStats) bOverall = b.playerStats.stats.overall;
            return bOverall - aOverall;
        })
    }

});