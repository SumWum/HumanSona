from Commands.editsona import EditSona
from Commands.sona import Sona


def setup(bot):
    bot.add_cog(Sona(bot))
    bot.add_cog(EditSona(bot))
