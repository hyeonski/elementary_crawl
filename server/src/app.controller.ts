import { Controller, Get, Query, Render, Res } from '@nestjs/common';
import { Response } from 'express';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  // @Get()
  // async getPostList(@Query('type') type: string, @Res() res: Response) {
  //   const view = await this.appService.getPostListViewName(type);
  //   const postType = await this.appService.getPostTypeByName(type);
  //   const posts = await this.appService.getPostsByPostType(postType);
  //   res.render(view, { count: posts.length, posts });
  // }

  @Get()
  @Render('list')
  async getPostList(@Query('type') type: string) {
    const postType = await this.appService.getPostTypeByName(type);
    const posts = await this.appService.getPostsByPostType(postType);
    return { type, count: posts.length, posts };
  }
}
