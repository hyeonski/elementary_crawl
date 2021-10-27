import { Column, Entity, PrimaryGeneratedColumn } from 'typeorm';

@Entity('school')
export class School {
  @PrimaryGeneratedColumn({ name: 'id', type: 'int' })
  id: number;

  @Column({ name: 'name', type: 'varchar', length: 30 })
  name: string;
}
