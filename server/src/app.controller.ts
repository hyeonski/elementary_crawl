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
  async getSchoolList(@Res() res: Response) {
    const schools = await this.appService.getSchools();
    return res.render('index', { schools });
  }

  @Get('/school/:id')
  async getSchoolPostList(
    @Param('id') id: number,
    @Query('type') type: string,
    @Res() res: Response,
  ) {
    const school = await this.appService.getSchoolById(id);
    const postTypes = new Map<string, string>([
      ['notice', '공지사항'],
      ['parent_letter', '가정통신문'],
      ['school_meal_news', '급식 소식'],
      ['today_school_meal', '오늘의 급식'],
    ]);
    let posts: Post[];

    if (!type) {
      posts = await this.appService.getPostsBySchool(school);
    } else if (postTypes.has(type)) {
      const postType = await this.appService.getPostTypeByName(
        postTypes.get(type),
      );
      posts = await this.appService.getPostsBySchool(school, postType);
    } else {
      throw new NotFoundException();
    }
    const lastUpdate =
      posts.length > 0 ? posts[0].updatedAt.toLocaleString() : null;

    return res.render('list_post', {
      school,
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
