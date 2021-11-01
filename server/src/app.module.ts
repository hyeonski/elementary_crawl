import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AttachedFile } from './entities/attached-file.entity';
import { PostType } from './entities/post-type.entity';
import { Post } from './entities/post.entity';
import { School } from './entities/school.entity';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: process.env.DB_HOST,
      port: Number(process.env.DB_PORT),
      username: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      entities: [PostType, Post, AttachedFile, School],
      synchronize: false,
    }),
    TypeOrmModule.forFeature([PostType, Post, AttachedFile, School]),
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
