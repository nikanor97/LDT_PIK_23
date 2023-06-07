import asyncio
import random

import uvloop
from fastapi import UploadFile

import settings
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import ProjectBase, UserRoleBase
from src.server.constants import fittings_config, FittingCreate
from src.server.projects.models import ProjectCreate
from src.server.users.endpoints import UsersEndpoints
from src.server.projects.endpoints import ProjectsEndpoints
from src.server.users.models import UserCreate, UserLogin


lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed elit ligula, gravida sed hendrerit sed, congue ut justo. Pellentesque vel volutpat dolor. Vivamus vestibulum, arcu mattis sollicitudin luctus, nunc ante convallis elit, vel fringilla orci est at sapien. Etiam a ultricies turpis. Duis ac libero eget urna tincidunt scelerisque. Maecenas in elementum ipsum. In vitae lacus in ligula molestie porta nec id lectus. Proin ac purus feugiat, suscipit felis sed, convallis mi. Suspendisse potenti. Sed imperdiet bibendum mattis. Sed id elementum lectus, id suscipit libero. In hac habitasse platea dictumst. Proin eget tellus lobortis elit euismod tempus sit amet sed enim. Integer a euismod nunc. Vivamus consectetur sollicitudin lacus, et tristique metus semper in. Donec rhoncus aliquet quam ut semper. Proin congue, nibh quis suscipit placerat, est tellus egestas augue, non fermentum risus neque sit amet purus. Maecenas ultricies interdum sagittis. Suspendisse et neque erat. Vestibulum maximus, ante et cursus commodo, ipsum est mattis diam, vitae dignissim tellus ipsum molestie nibh. Sed vel odio consequat, rutrum massa non, tristique erat. Sed in pulvinar tortor. Aliquam et sodales ex. Vivamus urna leo, aliquam at felis eu, luctus pretium est. Fusce vitae ultrices diam, nec egestas elit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Duis at volutpat magna. Duis vel blandit ex, et cursus odio. Nunc dictum porta accumsan. Aenean at sapien elit. Sed felis massa, molestie eu vehicula tincidunt, sodales at dolor. Nullam ut vulputate magna, sed consectetur leo. Vivamus vitae augue et erat tempus suscipit quis pellentesque augue. Quisque malesuada scelerisque mi, at sollicitudin ipsum condimentum eu. Duis fermentum tempor sollicitudin. Cras lacinia et erat in egestas. Aenean vitae neque nec odio accumsan porttitor. In hac habitasse platea dictumst. Nam vestibulum lobortis erat quis dignissim. Cras congue justo mi, id efficitur neque rutrum vitae. Nullam non eleifend magna, sed placerat purus. Donec bibendum purus malesuada risus tempor, vitae pellentesque purus faucibus. Donec nec nunc neque. Cras quis hendrerit tellus, posuere volutpat turpis. Sed et dolor sem. Praesent non dapibus est. Suspendisse et sagittis nisl. Duis posuere luctus consequat. Proin dignissim tempus felis ut semper. Vivamus mauris metus, efficitur dapibus interdum vitae, tempor vel velit. In tempus libero massa, sit amet porttitor nisi congue imperdiet. Vivamus in diam sed massa efficitur fermentum. Sed turpis justo, sagittis non volutpat eget, posuere quis lectus. Aliquam eget magna magna. Aenean nec nulla lacus."""


async def init_db():
    main_db_manager = MainDbManager(db_name_prefix=settings.DB_NAME_PREFIX)
    ue = UsersEndpoints(main_db_manager)
    pe = ProjectsEndpoints(main_db_manager)

    try:
        await ue.create_user(UserCreate(
            name='Sergey', email='serbudnik', password='qwerty'
        ))
    except:
        pass

    try:
        await ue.create_user(UserCreate(
            name='ivan', email='ivan@mail.ru', password='vano'
        ))
    except:
        pass

    try:
        await ue.create_user(UserCreate(
            name='Artem', email='art.shakhov3@mail.ru', password='test'
        ))
    except:
        pass


    token_sergey = await ue.login_for_access_token(UserLogin(username='serbudnik', password='qwerty'))
    token_ivan = await ue.login_for_access_token(UserLogin(username='ivan@mail.ru', password='vano'))
    token_artem = await ue.login_for_access_token(UserLogin(username='art.shakhov3@mail.ru', password='test'))

    user_sergey = await ue.get_current_user(token_sergey.access_token)
    user_ivan = await ue.get_current_user(token_ivan.access_token)
    user_artem = await ue.get_current_user(token_artem.access_token)

    lorem_words = lorem_ipsum.split(' ')

    await pe.create_fittings(fittings_config)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        app = loop.run_until_complete(init_db())
    finally:
        loop.close()
