import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AttachedFile } from './entities/attached-file.entity';
import { PostType } from './entities/post-type.entity';
import { Post } from './entities/post.entity';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: '1234',
      database: 'elementary',
      entities: [PostType, Post, AttachedFile],
      synchronize: false,
    }),
    TypeOrmModule.forFeature([PostType, Post, AttachedFile]),
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
