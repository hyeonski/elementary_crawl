import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { EntityNotFoundError, Repository } from 'typeorm';
import { PostType } from './entities/post-type.entity';
import { Post } from './entities/post.entity';
import { School } from './entities/school.entity';

@Injectable()
export class AppService {
  constructor(
    @InjectRepository(Post) private readonly postRepository: Repository<Post>,
    @InjectRepository(PostType)
    private readonly postTypeRepository: Repository<PostType>,
    @InjectRepository(School)
    private readonly schoolRepository: Repository<School>,
  ) {}

  async getSchools(): Promise<School[]> {
    return await this.schoolRepository.find({
      order: { name: 'ASC' },
    });
  }

  async getSchoolById(id: number): Promise<School> {
    try {
      return await this.schoolRepository.findOneOrFail({
        where: { id },
      });
    } catch (e) {
      if (e instanceof EntityNotFoundError) {
        throw new NotFoundException();
      } else throw e;
    }
  }

  async getPostsBySchool(school: School, type?: PostType): Promise<Post[]> {
    if (type) {
      return await this.postRepository.find({
        where: { school, postType: type },
        order: { uploadAt: 'DESC' },
      });
    } else {
      return await this.postRepository.find({
        where: { school },
        order: { uploadAt: 'DESC' },
      });
    }
  }

  async getPostTypeByName(name: string): Promise<PostType> {
    return await this.postTypeRepository.findOne({ where: { name } });
  }

  async getPostById(id: number): Promise<Post> {
    try {
      return await this.postRepository.findOneOrFail({
        where: { id },
        relations: ['postType', 'school', 'attachedFiles'],
      });
    } catch (e) {
      if (e instanceof EntityNotFoundError) {
        throw new NotFoundException();
      } else throw e;
    }
  }

  convertFileSizeToString(size: number): string {
    if (size < 1024) {
      return `${size} B`;
    } else if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(2)} KB`;
    } else if (size < 1024 * 1024 * 1024) {
      return `${(size / 1024 / 1024).toFixed(2)} MB`;
    } else {
      return `${(size / 1024 / 1024 / 1024).toFixed(2)} GB`;
    }
  }
}
