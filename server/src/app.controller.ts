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
import { Post } from './entities/post.entity';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getPostList(@Query('type') type: string, @Res() res: Response) {
    const postTypes = [
      'notice',
      'parent_letter',
      'school_meal',
      'school_meal_menu',
    ];
    let posts: Post[];

    if (!type) {
      posts = await this.appService.getPosts();
    } else if (postTypes.includes(type)) {
      const postType = await this.appService.getPostTypeByName(type);
      posts = await this.appService.getPostsByPostType(postType);
    } else {
      throw new NotFoundException();
    }
    const lastUpdate =
      posts.length > 0 ? posts[0].updatedAt.toLocaleString() : null;

    return res.render('list_post', {
      type,
      count: posts.length,
      lastUpdate,
      posts,
    });
  }

  @Get('/post/:id')
  async getPost(@Param('id') id: number, @Res() res: Response) {
    const post: any = await this.appService.getPostById(id);
    for (const file of post.attachedFiles) {
      file.size = this.appService.convertFileSizeToString(file.size);
    }
    return res.render('post', post);
  }
}
