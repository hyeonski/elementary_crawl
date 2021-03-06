import {
  Column,
  Entity,
  JoinColumn,
  ManyToOne,
  OneToMany,
  PrimaryColumn,
} from 'typeorm';
import { AttachedFile } from './attached-file.entity';
import { PostType } from './post-type.entity';
import { School } from './school.entity';

@Entity('post')
export class Post {
  @PrimaryColumn({ name: 'id', type: 'int' })
  id: number;

  @ManyToOne(() => School)
  @JoinColumn({ name: 'school_id', referencedColumnName: 'id' })
  school: School;

  @ManyToOne(() => PostType)
  @JoinColumn({ name: 'post_type_id', referencedColumnName: 'id' })
  postType: PostType;

  @Column({ name: 'data_key', type: 'varchar', length: 20 })
  dataKey: string;

  @Column({ name: 'author', type: 'varchar', length: 30 })
  author: string;

  @Column({ name: 'upload_at', type: 'date' })
  uploadAt: Date;

  @Column({ name: 'title', type: 'varchar', length: 100 })
  title: string;

  @Column({ name: 'content', type: 'mediumtext', nullable: true })
  content: string;

  @Column({ name: 'updated_at', type: 'timestamp' })
  updatedAt: Date;

  @OneToMany(() => AttachedFile, (attachedFile) => attachedFile.post)
  attachedFiles: AttachedFile[];
}
