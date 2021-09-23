import { Controller, Get, Param, Query, Render } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  @Render('list')
  async getPostList(@Query('type') type: string) {
    const postType = await this.appService.getPostTypeByName(type);
    const posts = await this.appService.getPostsByPostType(postType);
    return { type, count: posts.length, posts };
  }

  @Get('/post/:id')
  @Render('post')
  async getPost(@Param('id') id: number) {
    const post = await this.appService.getPostById(id);
    return post;
  }
}
