import { Column, Entity, PrimaryGeneratedColumn } from 'typeorm';

@Entity('post_type')
export class PostType {
  @PrimaryGeneratedColumn({ name: 'id', type: 'int' })
  id: number;

  @Column({ name: 'name', type: 'varchar', length: 20 })
  name: string;
}
