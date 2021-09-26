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

    let lastUpdate: string;
    if (posts.length > 0) {
      lastUpdate = `${posts[0].updatedAt.toLocaleDateString()} ${posts[0].updatedAt.toLocaleTimeString()}`;
    }
    return {
      type,
      lastUpdate,
      count: posts ? posts.length : 0,
      posts,
    };
  }

  @Get('/post/:id')
  @Render('post')
  async getPost(@Param('id') id: number) {
    const post: any = await this.appService.getPostById(id);
    for (const file of post.attachedFiles) {
      file.size = this.appService.convertFileSizeToString(file.size);
    }
    return post;
  }
}
