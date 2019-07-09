from .sona import Sona
from .editsona import EditSona

def setup(bot):
    bot.add_cog(Sona(bot))
    bot.add_cog(EditSona(bot))
