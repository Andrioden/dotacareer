from google.appengine.ext import ndb


class Player(ndb.Model):
    userid = ndb.StringProperty(required=True)
    nick = ndb.StringProperty(required=True)
    skill = ndb.IntegerProperty(required=True)
    team = ndb.KeyProperty(kind='Team')

    def get_data_nick_and_id(self):
        return {
            'id': self.key.id(),
            'nick': self.nick
        }

    def get_data(self, detail_level="simple"):
        return {
            'id': self.key.id(),
            'nick': self.nick,
            'skill': self.skill,
            'team': self.team.get().get_data(detail_level) if self.team else None
        }


class Team(ndb.Model):
    name = ndb.StringProperty(required=True)
    owner = ndb.KeyProperty(kind=Player, required=True)

    def get_data(self, detail_level="simple"):
        data = {
            'id': self.key.id(),
            'name': self.name,
            'owner': self.owner.get().get_data_nick_and_id()
        }
        if detail_level == "full":
            data.update({
                'applications': [team_app.get_data() for team_app in TeamApplication.query(TeamApplication.team == self.key)],
                'members': [player.get_data_nick_and_id() for player in Player.query(Player.team == self.key)]
            })

        return data


class TeamApplication(ndb.Model):
    team = ndb.KeyProperty(kind=Team, required=True)
    player = ndb.KeyProperty(kind=Player, required=True)
    text = ndb.StringProperty(required=True)

    def get_data(self):
        return {
            'id': self.key.id(),
            'player': self.player.get().get_data(),
            'text': self.text
        }