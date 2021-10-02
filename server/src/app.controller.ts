import {
  Controller,
  Get,
  NotFoundException,
  Param,
  Query,
  Res,
} from '@nestjs/common';
import { Response } from 'express';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getPostList(@Query('type') type: string, @Res() res: Response) {
    const postTypes = ['notice', 'parent_letter', 'school_meal'];
    let lastUpdate;

    if (!type) type = 'notice';

    if (type === 'school_meal_menu') {
      const menus = await this.appService.getSchoolMealMenus();
      lastUpdate =
        menus.length > 0 ? menus[0].updatedAt.toLocaleString() : null;

      return res.render('list_menu', {
        type,
        count: menus.length,
        lastUpdate,
        menus,
      });
    } else if (postTypes.includes(type)) {
      const postType = await this.appService.getPostTypeByName(type);
      const posts = await this.appService.getPostsByPostType(postType);
      lastUpdate =
        posts.length > 0 ? posts[0].updatedAt.toLocaleString() : null;

      return res.render('list_post', {
        type,
        count: posts.length,
        lastUpdate,
        posts,
      });
    } else {
      throw new NotFoundException();
    }
  }

  @Get('/post/:id')
  async getPost(@Param('id') id: number, @Res() res: Response) {
    const post: any = await this.appService.getPostById(id);
    for (const file of post.attachedFiles) {
      file.size = this.appService.convertFileSizeToString(file.size);
    }
    return res.render('post', post);
  }

  @Get('/menu/:id')
  async getMenu(@Param('id') id: number, @Res() res: Response) {
    const menu = await this.appService.getSchoolMealMenuById(id);
    return res.render('menu', menu);
  }
}
